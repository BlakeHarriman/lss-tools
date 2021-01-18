# lib
import statistics

# local
import timeutil


def get_attempt_id(time_xml_node):
    return int(time_xml_node.attrib['id'])


def get_time_iter_ms(segment_xml_root, min_attempt_id=None, comparison='GameTime'):
    times = segment_xml_root.findall('SegmentHistory/Time')
    if (type(min_attempt_id) is int):
        times = filter(lambda x: get_attempt_id(x) > min_attempt_id, times)
    game_times_raw = map(lambda x: x.find(comparison), times)
    game_time_elements = filter(lambda x: x is not None, game_times_raw)
    game_times_text = map(lambda x: x.text, game_time_elements)
    parsed_times = map(timeutil.parse_time, game_times_text)
    return map(timeutil.to_milliseconds, parsed_times)


def z_score(value, mean, deviation):
    return (value - mean) / deviation


def remove_outliers(times, mean, deviation, zscore_cutoff=None):  # Calc Z Score and remove if outlier
    n = 0
    while n in range(len(times)):
        absolute_z_score = abs(z_score(times[n], mean, deviation))
        if (absolute_z_score > zscore_cutoff):
            times.pop(n)
        else:
            n += 1

    return (int(statistics.mean(times)), int(statistics.median(times)), int(statistics.stdev(times)))


class Segment:

    def __init__(self, xml_root):
        self.name = xml_root.find('Name').text
        self.__xml_root__ = xml_root

    def get_gold_time(self, comparison='GameTime'):
        search_key = 'BestSegmentTime/{}'.format(comparison)
        gold_string = self.__xml_root__.find(search_key).text
        time_tuple = timeutil.parse_time(gold_string)
        return timeutil.to_milliseconds(time_tuple)

    def get_summary(self, min_attempt_id=None, comparison='GameTime', zscore_cutoff=None):
        times = list(get_time_iter_ms(self.__xml_root__,
                                      comparison=comparison, min_attempt_id=min_attempt_id))
        mean = int(statistics.mean(times))
        median = int(statistics.median(times))
        deviation = int(statistics.stdev(times))
        if type(zscore_cutoff) is int:
            mean, median, deviation = remove_outliers(times, mean, deviation, zscore_cutoff=zscore_cutoff)
        stats = dict([
            ('mean', mean),
            ('median', median),
            ('deviation', deviation)
        ])

        return dict([
            ('name', self.name),
            ('gold', self.get_gold_time(comparison=comparison)),
            ('stats', stats)
        ])
