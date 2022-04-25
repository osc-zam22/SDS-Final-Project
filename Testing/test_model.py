import unittest
from model import increment_likes

class testModel(unittest.TestCase):
    

    # tests if the likes increment accordingly
    def test_increment_likes(self):
        self.assertEquals(increment_likes(0) , 1)
        self.assertNotEqual(increment_likes(0) , 0)
        self.assertRaises(TypeError , increment_likes , "not an int")
        self.assertRaises(ValueError , increment_likes , -1)