import requests as req
from db import TokenStore

class Client:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.db = TokenStore()
        self.session = req.Session()
        self.is_authenticated = False
        self.refresh_access_token()

    def logout(self):
        if not self.is_authenticated:
            print("No Account to logout")
            return

        token = self.db.load()
        print(token)

        res = self.session.post(
            f"{self.base_url}/api/users/logout/",
            json={"refresh": token},
        )

        if res.ok:
            try:
                print(res.json())
            except ValueError:
                print("Logout successful, but server returned no JSON.")

            self.db.delete()
            self.is_authenticated = False

        else:
            print("Logout failed:", res.status_code)
            print("error",res.json())

    def register(self):
        username = input("Username: ")
        password = input("Password: ")
        res = self.session.post(
            f"{self.base_url}/api/users/register/",
            json={"username": username, "password": password},
        )
        if res.status_code == 201:
            print(res.json())
        else:
            print("Request failed:", res.status_code)

    def delete_book(self):
        id_num = int(input("ID: "))
        res = self.session.delete(
            f"{self.base_url}/api/books/{id_num}/",
        )
        if res.status_code in(200,204):
            print(res)
            print("Delete successful.")
        else:
            print("Request failed:", res.status_code)
            print("Delete failed")

    def view_books(self):
        res = self.session.get(
            f"{self.base_url}/api/books/",
        )
        if res.status_code == 200:
            rev = sorted(res.json(),key=lambda x:x["id"],reverse=True)
            print(rev or "empty")
        else:
            print("Request failed:", res.status_code)

    def create_book(self):
        if not self.is_authenticated:
            self.login()
        title = input("Title: ").strip()
        author = input("author : ").strip()
        res = self.session.post(
            f"{self.base_url}/api/books/",
            json={"title": title, "author": author},
        )
        if res.status_code == 201:
            print(res.json())
        else:
            print("Request failed:", res.status_code)

    def refresh_access_token(self):
        """Use the saved refresh token to get a new access token."""
        refresh_token = self.db.load()

        if not refresh_token:
            return False

        try:
            res = self.session.post(
                f"{self.base_url}/api/users/refresh/",
                json={
                    "refresh": refresh_token
                },
                timeout=10,
            )
        except req.RequestException as e:
            print("Network error:", e)
            return False

        if res.status_code != 200:
            print("Refresh failed:", res.status_code)
            # Refresh token is probably expired/invalid.
            return False

        tokens = res.json()

        access_token = tokens["access"]

        # In case refresh-token rotation is enabled
        if "refresh" in tokens:
            self.db.save(tokens["refresh"])

        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        self.is_authenticated = True
        return True

    def login(self):
        username = input("Username: ")
        password = input("Password: ")

        try:
            res = self.session.post(
                f"{self.base_url}/api/users/login/",
                json={
                    "username": username,
                    "password": password,
                },
                timeout=10,
            )
            self.is_authenticated = True
        except req.RequestException as e:
            print("Network error:", e)
            return False

        if res.status_code != 200:
            print("Login failed:", res.status_code)
            return False

        tokens = res.json()

        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        # Save ONLY the refresh token
        self.db.save(refresh_token)

        # Keep access token in memory
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })

        return True

    def get_users(self):
        # First try using saved refresh token
        if not self.refresh_access_token():

            # No valid refresh token -> login
            if not self.login():
                return None

        try:
            res = self.session.get(
                f"{self.base_url}/api/users/",
                timeout=10,
            )
            print(res.json())
        except req.RequestException as e:
            print("Network error:", e)
            return None

        # Access token may have expired
        if res.status_code == 401:

            # Get a fresh access token
            if self.refresh_access_token():

                # Retry request
                res = self.session.get(
                    f"{self.base_url}/api/users/",
                    timeout=10,
                )
            else:
                print("Authentication expired.")
                return None

        if res.status_code == 200:
            return res.json()

        print("Request failed:", res.status_code)
        return None

    def update_book(self):
        book_id = int(input("ID: "))
        title = input("Title: ")
        author = input("Author: ")

        if title == "" and author == "":
            return
        res = self.session.put(
            f"{self.base_url}/api/books/{book_id}/",
            json={"title": title, "author": author},
        )
        if res.json():
            print(res.json())
        else:
            print("Request failed:", res.status_code)

    def run(self):
        ops = [
            ("view",self.get_users),("login",self.login), ("register",self.register),
            ("create book",self.create_book),
            ("view books",self.view_books),("delete book",self.delete_book),("update book",self.update_book),
            ("logout",self.logout),("Exit",quit)
        ]

        while True:
            print("Main Menu".center(50,"_"))
            for i,(o,_) in enumerate(ops,1):
                print(f"{i}. {o.capitalize()}")
            cm = int(input("Choose: "))
            if 1 <= cm <= len(ops):
                ops[cm-1][1]()
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    client = Client()
    client.run()
