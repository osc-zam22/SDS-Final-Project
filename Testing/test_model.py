import unittest
from model import increment_num_ratings , increment_likes, rating

class testModel(unittest.TestCase):
    

    # tests if the likes increment accordingly
    def test_increment_likes(self):
        self.assertEquals(increment_likes(0) , 1)
        self.assertNotEqual(increment_likes(0) , 0)