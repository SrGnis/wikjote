from htmlobject import HTMLObject

class Processor:

    def __init__(self, object: HTMLObject, section_type: None | str = None):
        self.object = object
        self.section_type = section_type

        """ Returns a dict whit the name of the section and the contents
        """
    def run(self) -> dict:
        pass