def increment_likes(like):
    return like + 1

def increment_num_ratings(num_ratings):
    return num_ratings + 1

def rating(num_ratings , curr_ratings , new_rating):
    num_ratings = increment_num_ratings(num_ratings)
    return (curr_ratings + new_rating) / num_ratings 

