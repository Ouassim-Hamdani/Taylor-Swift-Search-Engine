from owlready2 import *
# CANCELED APPROACH OWL IS HORRIBLE
# Create a new ontology
onto = get_ontology("taylorswift_ontology.owl")

with onto:
    # Classes
    class Song(Thing): pass
    class Album(Thing): pass
    class Segment(Thing): pass
    class Emotion(Thing): pass
    class Theme(Thing): pass

    # Relations
    class belongsTo(Song >> Album): pass
    class contains(Song >> Segment): pass
    class expresses(Segment >> Emotion): pass
    class dealsWith(Segment >> Theme): pass

    # Attributes
    class title(Song >> str): pass
    class name(Album >> str): pass
    class lyrics(Segment >> str): pass
    class name(Emotion >> str): pass 
    class name(Theme >> str): pass 

onto.save("../../data/taylorswift_ontology.owl")