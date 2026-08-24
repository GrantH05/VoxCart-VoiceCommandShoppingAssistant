import unittest

from core.nlp import parse_command


class NLPTests(unittest.TestCase):
    def test_add_water_quantity_unit(self):
        c = parse_command("Add 2 bottles of water")
        self.assertEqual(c.action, "add")
        self.assertEqual(c.item, "Water")
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.unit, "bottle")

    def test_need_oranges(self):
        c = parse_command("I need 5 oranges")
        self.assertEqual((c.action, c.item, c.quantity), ("add", "Oranges", 5))

    def test_remove(self):
        c = parse_command("Remove milk from my list")
        self.assertEqual(c.action, "remove")
        self.assertEqual(c.item, "Milk")

    def test_search_price(self):
        c = parse_command("Find toothpaste under $5")
        self.assertEqual(c.action, "search")
        self.assertEqual(c.item, "Toothpaste")
        self.assertEqual(c.max_price, 5.0)

    def test_search_organic(self):
        c = parse_command("Find organic apples")
        self.assertEqual(c.action, "search")
        self.assertEqual(c.item, "Organic Apples")

    def test_hindi(self):
        c = parse_command("मुझे पांच संतरे चाहिए")
        self.assertEqual(c.action, "add")
        self.assertEqual(c.item, "Oranges")
        self.assertEqual(c.quantity, 5)

    def test_spanish(self):
        c = parse_command("Agrega dos botellas de agua")
        self.assertEqual(c.action, "add")
        self.assertEqual(c.item, "Water")
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.unit, "bottle")

    def test_french(self):
        c = parse_command("Ajoute deux bouteilles d'eau")
        self.assertEqual(c.action, "add")
        self.assertEqual(c.quantity, 2)
        self.assertEqual(c.item, "Water")

    def test_update(self):
        c = parse_command("Change milk quantity to 3")
        self.assertEqual(c.action, "update")
        self.assertEqual(c.item, "Milk")
        self.assertEqual(c.quantity, 3)


if __name__ == "__main__":
    unittest.main()
