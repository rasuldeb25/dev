#Project 7: Demonstaration of working wiht a modules (converter.py is a follow-up file)
#We use modules to better organize our code, instead of writing all the functions in one file, we define them in 
#another file and simply import it.
import converter #imports entire module
from converter import kg_to_lbs #imports specefic function out of that module

print(converter.kg_to_lbs(70))
kg_to_lbs(70)