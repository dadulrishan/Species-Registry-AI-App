import requests
import sys
import json
from datetime import datetime
import uuid

class MonkeyRegistryAPITester:
    def __init__(self, base_url="https://simian-tracker.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_monkeys = []  # Track created monkeys for cleanup

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if method == 'POST' and 'monkey_id' in response_data:
                        self.created_monkeys.append(response_data['monkey_id'])
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_create_monkey_valid(self):
        """Test creating a monkey with valid data"""
        monkey_data = {
            "name": f"TestMonkey_{datetime.now().strftime('%H%M%S')}",
            "species": "capuchin",
            "age_years": 5,
            "favourite_fruit": "banana",
            "last_checkup_at": "2024-01-15T10:30:00"
        }
        return self.run_test("Create Valid Monkey", "POST", "monkeys", 201, monkey_data)

    def test_create_monkey_invalid_name_short(self):
        """Test creating monkey with name too short"""
        monkey_data = {
            "name": "A",  # Too short
            "species": "capuchin",
            "age_years": 5,
            "favourite_fruit": "banana"
        }
        return self.run_test("Create Monkey - Name Too Short", "POST", "monkeys", 422, monkey_data)

    def test_create_monkey_invalid_name_long(self):
        """Test creating monkey with name too long"""
        monkey_data = {
            "name": "A" * 50,  # Too long
            "species": "capuchin", 
            "age_years": 5,
            "favourite_fruit": "banana"
        }
        return self.run_test("Create Monkey - Name Too Long", "POST", "monkeys", 422, monkey_data)

    def test_create_monkey_invalid_age_high(self):
        """Test creating monkey with age too high"""
        monkey_data = {
            "name": f"TestMonkey_{datetime.now().strftime('%H%M%S')}",
            "species": "capuchin",
            "age_years": 50,  # Too high
            "favourite_fruit": "banana"
        }
        return self.run_test("Create Monkey - Age Too High", "POST", "monkeys", 422, monkey_data)

    def test_create_monkey_invalid_age_negative(self):
        """Test creating monkey with negative age"""
        monkey_data = {
            "name": f"TestMonkey_{datetime.now().strftime('%H%M%S')}",
            "species": "capuchin",
            "age_years": -1,  # Negative
            "favourite_fruit": "banana"
        }
        return self.run_test("Create Monkey - Negative Age", "POST", "monkeys", 422, monkey_data)

    def test_create_marmoset_invalid_age(self):
        """Test creating marmoset with age > 22"""
        monkey_data = {
            "name": f"TestMarmoset_{datetime.now().strftime('%H%M%S')}",
            "species": "marmoset",
            "age_years": 25,  # Too high for marmoset
            "favourite_fruit": "grape"
        }
        return self.run_test("Create Marmoset - Age Too High", "POST", "monkeys", 422, monkey_data)

    def test_create_marmoset_valid_age(self):
        """Test creating marmoset with valid age"""
        monkey_data = {
            "name": f"TestMarmoset_{datetime.now().strftime('%H%M%S')}",
            "species": "marmoset",
            "age_years": 20,  # Valid for marmoset
            "favourite_fruit": "grape"
        }
        return self.run_test("Create Marmoset - Valid Age", "POST", "monkeys", 201, monkey_data)

    def test_create_duplicate_name_same_species(self):
        """Test creating monkey with duplicate name in same species"""
        # First create a monkey
        monkey_data = {
            "name": f"DuplicateTest_{datetime.now().strftime('%H%M%S')}",
            "species": "macaque",
            "age_years": 8,
            "favourite_fruit": "apple"
        }
        success, _ = self.run_test("Create Original Monkey", "POST", "monkeys", 201, monkey_data)
        
        if success:
            # Try to create another with same name and species
            return self.run_test("Create Duplicate Name Same Species", "POST", "monkeys", 400, monkey_data)
        return False, {}

    def test_create_duplicate_name_different_species(self):
        """Test creating monkey with same name but different species (should work)"""
        base_name = f"SameName_{datetime.now().strftime('%H%M%S')}"
        
        # Create first monkey
        monkey1_data = {
            "name": base_name,
            "species": "howler",
            "age_years": 10,
            "favourite_fruit": "mango"
        }
        success, _ = self.run_test("Create First Monkey", "POST", "monkeys", 201, monkey1_data)
        
        if success:
            # Create second monkey with same name but different species
            monkey2_data = {
                "name": base_name,
                "species": "capuchin",  # Different species
                "age_years": 7,
                "favourite_fruit": "banana"
            }
            return self.run_test("Create Same Name Different Species", "POST", "monkeys", 201, monkey2_data)
        return False, {}

    def test_list_all_monkeys(self):
        """Test listing all monkeys"""
        return self.run_test("List All Monkeys", "GET", "monkeys", 200)

    def test_list_monkeys_with_species_filter(self):
        """Test listing monkeys with species filter"""
        return self.run_test("List Monkeys - Species Filter", "GET", "monkeys", 200, params={"species": "capuchin"})

    def test_list_monkeys_with_search(self):
        """Test listing monkeys with search parameter"""
        return self.run_test("List Monkeys - Search", "GET", "monkeys", 200, params={"search": "George"})

    def test_get_specific_monkey(self):
        """Test getting a specific monkey by ID"""
        # First create a monkey to get
        monkey_data = {
            "name": f"GetTest_{datetime.now().strftime('%H%M%S')}",
            "species": "macaque",
            "age_years": 12,
            "favourite_fruit": "orange"
        }
        success, response = self.run_test("Create Monkey for Get Test", "POST", "monkeys", 201, monkey_data)
        
        if success and 'monkey_id' in response:
            monkey_id = response['monkey_id']
            return self.run_test("Get Specific Monkey", "GET", f"monkeys/{monkey_id}", 200)
        return False, {}

    def test_get_nonexistent_monkey(self):
        """Test getting a non-existent monkey"""
        fake_id = str(uuid.uuid4())
        return self.run_test("Get Non-existent Monkey", "GET", f"monkeys/{fake_id}", 404)

    def test_update_monkey(self):
        """Test updating a monkey"""
        # First create a monkey to update
        monkey_data = {
            "name": f"UpdateTest_{datetime.now().strftime('%H%M%S')}",
            "species": "howler",
            "age_years": 15,
            "favourite_fruit": "papaya"
        }
        success, response = self.run_test("Create Monkey for Update Test", "POST", "monkeys", 201, monkey_data)
        
        if success and 'monkey_id' in response:
            monkey_id = response['monkey_id']
            update_data = {
                "age_years": 16,
                "favourite_fruit": "coconut"
            }
            return self.run_test("Update Monkey", "PUT", f"monkeys/{monkey_id}", 200, update_data)
        return False, {}

    def test_update_nonexistent_monkey(self):
        """Test updating a non-existent monkey"""
        fake_id = str(uuid.uuid4())
        update_data = {"age_years": 10}
        return self.run_test("Update Non-existent Monkey", "PUT", f"monkeys/{fake_id}", 404, update_data)

    def test_delete_monkey(self):
        """Test deleting a monkey"""
        # First create a monkey to delete
        monkey_data = {
            "name": f"DeleteTest_{datetime.now().strftime('%H%M%S')}",
            "species": "capuchin",
            "age_years": 6,
            "favourite_fruit": "strawberry"
        }
        success, response = self.run_test("Create Monkey for Delete Test", "POST", "monkeys", 201, monkey_data)
        
        if success and 'monkey_id' in response:
            monkey_id = response['monkey_id']
            # Remove from cleanup list since we're intentionally deleting it
            if monkey_id in self.created_monkeys:
                self.created_monkeys.remove(monkey_id)
            return self.run_test("Delete Monkey", "DELETE", f"monkeys/{monkey_id}", 200)
        return False, {}

    def test_delete_nonexistent_monkey(self):
        """Test deleting a non-existent monkey"""
        fake_id = str(uuid.uuid4())
        return self.run_test("Delete Non-existent Monkey", "DELETE", f"monkeys/{fake_id}", 404)

    def cleanup_created_monkeys(self):
        """Clean up monkeys created during testing"""
        print(f"\n🧹 Cleaning up {len(self.created_monkeys)} created monkeys...")
        for monkey_id in self.created_monkeys:
            try:
                response = requests.delete(f"{self.api_url}/monkeys/{monkey_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up monkey {monkey_id[:8]}...")
                else:
                    print(f"⚠️  Failed to clean up monkey {monkey_id[:8]}...")
            except Exception as e:
                print(f"❌ Error cleaning up monkey {monkey_id[:8]}: {e}")

def main():
    print("🐒 Starting Monkey Registry API Tests...")
    print("=" * 50)
    
    tester = MonkeyRegistryAPITester()
    
    # Run all tests
    test_methods = [
        tester.test_api_root,
        tester.test_create_monkey_valid,
        tester.test_create_monkey_invalid_name_short,
        tester.test_create_monkey_invalid_name_long,
        tester.test_create_monkey_invalid_age_high,
        tester.test_create_monkey_invalid_age_negative,
        tester.test_create_marmoset_invalid_age,
        tester.test_create_marmoset_valid_age,
        tester.test_create_duplicate_name_same_species,
        tester.test_create_duplicate_name_different_species,
        tester.test_list_all_monkeys,
        tester.test_list_monkeys_with_species_filter,
        tester.test_list_monkeys_with_search,
        tester.test_get_specific_monkey,
        tester.test_get_nonexistent_monkey,
        tester.test_update_monkey,
        tester.test_update_nonexistent_monkey,
        tester.test_delete_monkey,
        tester.test_delete_nonexistent_monkey
    ]
    
    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            tester.tests_run += 1

    # Cleanup
    tester.cleanup_created_monkeys()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())