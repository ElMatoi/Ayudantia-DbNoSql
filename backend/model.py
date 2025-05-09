from neomodel import StructureNode, StringProperty, IntegerProperty


class Person(StructureNode):
    name = StringProperty(required=true)
    age= IntegerProperty(required=true)
    