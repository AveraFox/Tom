import aiofiles, json, statics
from typing import List, Optional, Dict, Any

# data classes to interact with the json data (I don't like working with dicts directly)

# class that stores a single report, 
# stores confirmation message, list of cheater steamids and points awarded for the report
class Report:
    def __init__(self, message: str, steamids: List[int], points: int):
        self.message: str = message
        self.steamids: List[int] = steamids
        self.points: int = points
    
    # creates a Report object from a json dict
    def from_json(json_report) -> Report:
        return Report(
            json_report["msg"], 
            json_report["steamids"],
            json_report["points"]
        )

    # creates a dict ready to be converted to json
    def to_json(self) -> Dict[str, Any]:
        return {
            "msg": self.message,
            "steamids": self.steamids,
            "points": self.points
        }

# class that represents a person reporting cheaters
# stores userid, list of Reports and steam profile id
class Reporter:
    def __init__(self, userid: str, reports: List[Report], profile_id: Optional[int]):
        self.userid: int = userid
        self.reports: List[Report] = reports
        self.profile_id: int = profile_id

    # creates a new report for this reporter
    def add_report(self, msg: str, points: int, steamids: List[int]): 
        self.reports.append(Report(msg, steamids, points))
    
    # looks for a report with the passed thread link and removes it
    # returns True or False depending on if it succeeded or not
    def remove_report(self, link: str) -> bool:
        report = self.find_report(link)
        if report:
            self.reports.remove(report)
            return True
        return False

    # looks for a report based on a thread link
    def find_report(self, thread_link: str) -> Optional[Report]: # could return None or a Report
        for report in self.reports:
            if thread_link in report.message:
                return report
        return None

    def from_json(userid: int, json_map: dict) -> Reporter:
        reports: List[Report] = []
        for report in json_map["reports"]:
            reports.append(Report.from_json(report))
        return Reporter(userid, reports, None)
    
    # sums up all the points of the reports of this reporter
    def points(self) -> int:
        points = 0
        for report in self.reports:
            points += report.points
        return points

    # creates a dict ready to be converted to json
    def to_json(self):
        return {
            "reports": list(map(lambda r: r.to_json(), self.reports)),
            "count": self.points(), # store total count aswell, is not used by the program but makes the json more usable on it's own
            "profile_id": self.profile_id
        }

class Reports:
    def __init__(self, reporters: Dict[str, Reporter]): 
        self._reporters: Dict[str, Reporter]  = reporters

    # gets the Reporter object for the given discord id, or creates a new empty one if it doesn't exist
    def get_or_create(self, reporter_id: int) -> Reporter:
        reporter_id = str(reporter_id)
        if reporter_id not in self._reporters:
            self.__reporters[reporter_id] = Reporter(reporter_id, [], 0, 0)
        return self._reporters[reporter_id]

    # gets the Reporter object for the given discord id, or None if it doesn't exist
    def get(self, reporter_id: int) -> Optional[Reporter]:
        reporter_id = str(reporter_id)
        if reporter_id in self._reporters:
            return self._reporters[reporter_id]
        
    # looks up if a cheater has been reported before, if yes returns the first Report
    def find_cheater(self, steamid: int) -> Optional[Report]:
        for reporter in self._reporters.values():
            for report in reporter.reports:
                if steamid in report.steamids:
                    return report
        return None

    # loads Report data from the data file
    async def load() -> Reports:
        async with aiofiles.open(statics.REPORTS_DATA_FILE) as f:
            reports = json.loads(await f.read())
            return Reports.from_json(reports)

    # saves Report data to the data file
    async def save(self):
        async with aiofiles.open(statics.REPORTS_DATA_FILE, "w") as f:
            await f.write(json.dumps(self.to_json(), indent=4, sort_keys=True))

    # makes a list sorted by report count descending and returns the first n items
    def get_top_n(self, n) -> List[Reporter]:
        reporter_list = list(self._reporters.values())
        reporter_list.sort(key=lambda r: r.points(), reverse=True)
        return reporter_list[:min(20, len(reporter_list))]
    
    # creates a Reports object from a json dict
    def from_json(json_map: dict) -> Reports:
        for key in json_map:
            json_map[key] = Reporter.from_json(int(key), json_map[key])
        return Reports(json_map)
    
    # creates a dict ready to be converted to json
    def to_json(self) -> Dict[str, dict]:
        reporters = {}
        for reporter in self._reporters:
            reporters[reporter] = self._reporters[reporter].to_json()
        return reporters


if __name__ == "__main__":
    # test code to mess about with the file format
    # only run when you execute this file directly
    with open("reports.json") as f:
        j = json.load(f)
        json_out = json.dumps(Reports.from_json(j).to_json(), indent=4, sort_keys=True)
        with open("reports.json", "w") as f:
            f.write(json_out)