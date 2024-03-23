import json


class StrJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except:
            return f"{type(obj).__name__}({obj})"
