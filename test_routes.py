#!/usr/bin/env python3
"""
Route Testing Script for Quiz App

This script tests all the routes in the quiz application to ensure
they are working correctly and all links are valid.

Usage: python test_routes.py
"""

import requests
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Base URL for the Flask application
BASE_URL = "http://localhost:5000"

class RouteTestError(Exception):
    """Custom exception for route testing errors"""
    pass

class RouteChecker:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.routes_tested = set()
        self.failed_routes = []

    def test_route(self, path, expected_status=200, method='GET', data=None):
        """Test a single route"""
        url = urljoin(self.base_url, path)

        try:
            if method.upper() == 'POST':
                response = self.session.post(url, data=data)
            else:
                response = self.session.get(url)

            self.routes_tested.add(path)

            if response.status_code == expected_status:
                print(f"✅ {method} {path} - Status: {response.status_code}")
                return response
            else:
                print(f"❌ {method} {path} - Expected: {expected_status}, Got: {response.status_code}")
                self.failed_routes.append(f"{method} {path}")
                return response

        except requests.exceptions.ConnectionError:
            print(f"❌ {method} {path} - Connection failed (Is the server running?)")
            self.failed_routes.append(f"{method} {path}")
            return None
        except Exception as e:
            print(f"❌ {method} {path} - Error: {str(e)}")
            self.failed_routes.append(f"{method} {path}")
            return None

    def extract_links(self, html_content):
        """Extract links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        # Find all anchor tags with href attributes
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Skip external links and javascript links
            if href.startswith('http') or href.startswith('javascript:'):
                continue
            links.append(href)

        return links

    def test_all_routes(self):
        """Test all application routes"""
        print("🚀 Starting route testing...\n")

        # Test home page
        print("📍 Testing Home Page")
        response = self.test_route('/')
        if response:
            links = self.extract_links(response.text)
            print(f"   Found {len(links)} links: {links}")

        print("\n📍 Testing Authentication Routes")
        # Test login page
        login_response = self.test_route('/login')
        if login_response:
            links = self.extract_links(login_response.text)
            print(f"   Found {len(links)} links in login page: {links}")

        # Test register page
        register_response = self.test_route('/register')
        if register_response:
            links = self.extract_links(register_response.text)
            print(f"   Found {len(links)} links in register page: {links}")

        # Test logout (should redirect to login)
        self.test_route('/logout', expected_status=302)

        print("\n📍 Testing Protected Routes (should redirect to login)")
        # Test quiz page without authentication (should redirect)
        self.test_route('/quiz', expected_status=302)

        # Test quiz results without authentication (should redirect)
        self.test_route('/quiz_results', expected_status=302)

        print("\n📍 Testing Form Submissions")
        # Test empty login form (should stay on login page with errors)
        self.test_route('/login', method='POST', data={}, expected_status=200)

        # Test empty registration form (should stay on register page with errors)
        self.test_route('/register', method='POST', data={}, expected_status=200)

        print("\n📍 Testing Invalid Routes")
        # Test non-existent route
        self.test_route('/nonexistent', expected_status=404)

        # Summary
        print(f"\n📊 Test Summary")
        print(f"   ✅ Total routes tested: {len(self.routes_tested)}")
        print(f"   ❌ Failed routes: {len(self.failed_routes)}")

        if self.failed_routes:
            print("\n❌ Failed Routes:")
            for route in self.failed_routes:
                print(f"   - {route}")
            return False
        else:
            print("\n🎉 All tested routes are working correctly!")
            return True

    def test_template_links(self):
        """Test if template links are valid"""
        print("\n🔗 Testing Template Links")

        # Get home page and test its links
        response = self.test_route('/')
        if response:
            links = self.extract_links(response.text)
            for link in links:
                if link.startswith('/'):
                    print(f"   Testing link: {link}")
                    self.test_route(link)

        # Get login page and test its links
        response = self.test_route('/login')
        if response:
            links = self.extract_links(response.text)
            for link in links:
                if link.startswith('/'):
                    print(f"   Testing link: {link}")
                    self.test_route(link)

        # Get register page and test its links
        response = self.test_route('/register')
        if response:
            links = self.extract_links(response.text)
            for link in links:
                if link.startswith('/'):
                    print(f"   Testing link: {link}")
                    self.test_route(link)

def main():
    """Main function to run all tests"""
    print("🧪 Quiz App Route Testing")
    print("=" * 50)

    checker = RouteChecker()

    try:
        # Test all routes
        success = checker.test_all_routes()

        # Test template links
        checker.test_template_links()

        print("\n" + "=" * 50)

        if success and not checker.failed_routes:
            print("🎉 All tests passed! Your quiz app routes are working correctly.")
            sys.exit(0)
        else:
            print("❌ Some tests failed. Please check the issues above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
