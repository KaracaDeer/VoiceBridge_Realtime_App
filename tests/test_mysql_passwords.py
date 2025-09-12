#!/usr/bin/env python3
"""
MySQL Password Tester
"""
# type: ignore
# flake8: noqa
import mysql.connector
from mysql.connector import Error


def test_mysql_passwords():
    """Test common MySQL passwords"""
    print("🔐 MySQL Password Tester")
    print("=" * 40)

    # Common passwords to try
    common_passwords = [
        "",  # No password
        "password",
        "root",
        "admin",
        "123456",
        "mysql",
        "root123",
        "password123",
        "admin123",
        "1234",
        "qwerty",
        "letmein",
    ]

    print(f"🧪 Testing {len(common_passwords)} common passwords...")

    for i, password in enumerate(common_passwords, 1):
        try:
            print(f"[{i}/{len(common_passwords)}] Testing password: {'(empty)' if not password else '***'}")

            connection = mysql.connector.connect(host="localhost", user="root", password=password)

            if connection.is_connected():
                print(f"✅ SUCCESS! Password: {'(empty)' if not password else password}")
                print(f"💡 Use this line in your .env file:")
                if password:
                    print(f"MYSQL_PASSWORD={password}")
                else:
                    print("MYSQL_PASSWORD=")

                connection.close()
                return password

        except Error as e:
            if "Access denied" in str(e):
                print(f"❌ Wrong password: {'(empty)' if not password else '***'}")
            else:
                print(f"⚠️  Connection error: {e}")

    print("\n❌ No common passwords worked")
    print("💡 Check your password with MySQL Workbench or reset your password")
    return None


if __name__ == "__main__":
    test_mysql_passwords()
