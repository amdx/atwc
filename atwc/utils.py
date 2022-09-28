#   Copyright 2022 Archimedes Exhibitions GmbH
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

def dump(o):
    import json
    print(json.dumps(o, indent=2))


def extract_ids(o):
    ids = []
    if isinstance(o, dict):
        o = [o]

    for entry in o:
        if '@id' in entry:
            ids.append(entry['@id'])

    return ids
