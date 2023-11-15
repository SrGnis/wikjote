from processors.procesor import Processor


class LanguageProcessor(Processor):
    def run(self):
        return {
            "name": self.object.name,
            "type": self.section_type,
            "contents": None,
        }
