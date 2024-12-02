import aiofiles, json, statics
from typing import List, Optional, Dict

class Report:
    def __init__(self, message: str, steamids: List[int], points: int):
        self.message: str = message
        self.steamids: List[int] = steamids
        self.points: int = points
    
    def from_json(json_report):
        return Report(
            json_report["msg"], 
            json_report["steamids"],
            json_report["points"]
        )

    def to_json(self):
        return {
            "msg": self.message,
            "steamids": self.steamids,
            "points": self.points
        }

class Reporter:
    def __init__(self, userid: str, reports: List[Report], profile_id: Optional[int]):
        self.userid: int = userid
        self.reports: List[Report] = reports
        self.profile_id: int = profile_id

    def add_report(self, msg: str, points: int, steamids: List[int]):
        self.reports.append(Report(msg, steamids, points))
    
    def remove_report(self, link: str) -> bool:
        report = self.find_report(link)
        if report:
            self.reports.remove(report)
            return True
        return False

    def find_report(self, thread_link: str) -> Optional[Report]:
        for report in self.reports:
            if thread_link in report.message:
                return report
        return None

    def from_json(userid: int, json_map: dict):
        reports: List[Report] = []
        for report in json_map["reports"]:
            reports.append(Report.from_json(report))
        return Reporter(userid, reports, None)
    
    def points(self) -> int:
        points = 0
        for report in self.reports:
            points += report.points
        return points

    def to_json(self):
        return {
            "reports": list(map(lambda r: r.to_json(), self.reports)),
            "count": self.points(),
            "profile_id": self.profile_id
        }

class Reports:
    def __init__(self, reporters: Dict[str, Reporter]): 
        self._reporters: Dict[str, Reporter]  = reporters

    def get_or_create(self, reporter_id: int) -> Reporter:
        reporter_id = str(reporter_id)
        if reporter_id not in self._reporters:
            self.__reporters[reporter_id] = Reporter(reporter_id, [], 0, 0)
        return self._reporters[reporter_id]

    def get(self, reporter_id: int) -> Optional[Reporter]:
        reporter_id = str(reporter_id)
        if reporter_id in self._reporters:
            return self._reporters[reporter_id]
        
    def find_cheater(self, steamid: int) -> Optional[Report]:
        for reporter in self._reporters.values():
            for report in reporter.reports:
                if steamid in report.steamids:
                    return report
        return None

    async def load():
        async with aiofiles.open(statics.REPORTS_DATA_FILE) as f:
            reports = json.loads(await f.read())
            return Reports.from_json(reports)

    async def save(self):
        async with aiofiles.open(statics.REPORTS_DATA_FILE, "w") as f:
            await f.write(json.dumps(self.to_json(), indent=4, sort_keys=True))

    def get_top_n(self, n) -> List[Reporter]:
        reporter_list = list(self._reporters.values())
        reporter_list.sort(key=lambda r: r.points(), reverse=True)
        return reporter_list[:min(20, len(reporter_list))]
    
    def from_json(json_map: dict):
        for key in json_map:
            json_map[key] = Reporter.from_json(int(key), json_map[key])
        return Reports(json_map)
    
    def to_json(self) -> Dict[str, dict]:
        reporters = {}
        for reporter in self._reporters:
            reporters[reporter] = self._reporters[reporter].to_json()
        return reporters


if __name__ == "__main__":
    with open("reports.json") as f:
        j = json.load(f)
        json_out = json.dumps(Reports.from_json(j).to_json(), indent=4, sort_keys=True)
        with open("reports.json", "w") as f:
            f.write(json_out)