
from profanity_filter import ProfanityFilter

pf = ProfanityFilter()
string = 'Fuck this'

print(pf.censor(string))