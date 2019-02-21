#!/usr/bin/python3
# pack: pyinstaller --onefile smi_aoi_group.py

import sys
import os
import re
import string
import argparse
from collections import defaultdict

def strdict():
    return defaultdict(str)


def hash3d():
    return defaultdict(strdict)


def int_def(value):
    try:
        return int(value)
    except ValueError:
        return 0


def int_strip(value):
    try:
        return int(value.strip(string.ascii_letters))
    except ValueError:
        return 0


parser = argparse.ArgumentParser(description='Process smi export data.')
parser.add_argument('source', help='input file name')
args = parser.parse_args()

source = args.source
groupssource = source+".groups"
listoutfile = source+".list"
statsoutfile = source+".stats"
debugoutfile = source+".debug"

if not os.path.isfile(source) or os.path.getsize(source) == 0:
    sys.exit("Could not read data file or no content: %s" % source)

print('Processing data file...')
replace = re.compile(r"\D+")
infile = open(source, encoding='utf-8')
header = infile.readline().split("\t")
data = defaultdict(hash3d)
trial = hash3d()
aoi_names = hash3d()
for l in infile:
    cols = l.split("\t")
    if len(cols) >= 14 and cols[5] == 'Fixation':
        fix_start = float(cols[7]) - float(cols[1])
        data[cols[2]][cols[3]][int(cols[6])] = (fix_start, float(cols[9]), int_def(cols[13]), cols[12])
        trial[cols[2]][cols[3]] = (cols[1], int_strip(cols[0]))
        aoi_names[cols[2]][int_def(cols[13])] = re.sub(r'[.,]', '', cols[12])
with open(listoutfile, 'w') as lo:
    for stimulus, stimulus_data in sorted(aoi_names.items()):
        for index, name in sorted(stimulus_data.items()):
            if index:
                lo.write("{}, {}, {}\n".format(stimulus, index, name))

if not os.path.isfile(groupssource) or os.path.getsize(groupssource) == 0:
    sys.exit("Could not read group data file or no content: %s" % groupssource)

print('Processing groups...')
do = open(debugoutfile, 'w')
so = open(statsoutfile, 'w')
so.write("Stimulus\tAOI group\tParticipant\tTotal dwell time\tMean dwelltime per word\tTotal num fixation\tFirst fixation start\tFirst fixation duration\tFirst pass duration\tFirst pass mean dwelltime per word\t""First pass num fixations\tSecond pass start\tSecond pass duration\tSecond pass num fixations\tRe-readings duration\tRe-readings mean dwelltime per word\tTotal Skip\tNum regressions into\tSources regressions into\tNum regressions out of\tTargets regressions out of\tTrial no.\tTrial start time\tGroup word count\tGroup char count\n")
for line in open(groupssource):
    if len(line.strip()) <= 1:
        continue
    group = re.split(r"[\t ,]+", line.strip())
    if len(group) <= 1:
        continue
    stimulus = group.pop(0)
    print("Processing {}... ".format(stimulus), end="")
    max_group_index = int(max(group, key=int))
    group_word_count = len(group)
    group_char_count = 0
    group_str = ""
    for aoi in group:
        group_char_count += len(aoi_names[stimulus][int_def(aoi)])
        group_str += aoi_names[stimulus][int_def(aoi)] + " "
        if not len(aoi_names[stimulus][int_def(aoi)]):
            print('Warning: unknown AOI index {}! '.format(int_def(aoi)), end="")
    for participant, part_data in data[stimulus].items():
        (trial_start, trial_num) = trial[stimulus][participant]
        total_dwelltime = 0
        num_fix = 0
        first_fix_duration = 0
        first_pass_start = 0
        first_pass_end = 0
        first_pass_num_fix = 0
        first_pass_duration = 0
        second_pass_start = 0
        second_pass_end = 0
        second_pass_num_fix = 0
        second_pass_duration = 0
        last_fix_aoi = 0
        regressions_into = 0
        regressions_into_src = []
        regressions_outof = 0
        regressions_outof_tgt = []
        do.write("Stimulus {} Participant {} Trial no. {} Trial start time {} Group {} {} Group word count {} Group char count {} \n".format(stimulus, participant, trial_num, trial_start, group, group_str, group_word_count, group_char_count))
        if not len(aoi_names[stimulus][int_def(aoi)]):
            do.write("Warning: unknown AOI index {}!\n".format(int_def(aoi)))
        for fixation, fix_data in part_data.items():
            (start, duration, aoi_hit, aoi_name) = fix_data
            do.write("Fix {:>3}:\t {:>25}\t {:>4}\t{:>7.1f}\t{:>8}".format(fixation, aoi_name, aoi_hit, start, duration))
            if str(aoi_hit) in group:
                do.write(" <-")
                num_fix += 1
                total_dwelltime += duration
                if not first_pass_start:
                    first_pass_start = start
                    first_fix_duration = duration
                if first_pass_start and not first_pass_end:
                    first_pass_duration += duration
                    first_pass_num_fix += 1
                if not second_pass_start and first_pass_end:
                    second_pass_start = start
                if second_pass_start and not second_pass_end:
                    second_pass_duration += duration
                    second_pass_num_fix += 1
                if last_fix_aoi not in group and int_def(last_fix_aoi) > 0 and int_def(last_fix_aoi) > int_def(aoi_hit):
                    regressions_into += 1
                    regressions_into_src.append(last_fix_aoi)
            else:
                if first_pass_start and not first_pass_end and int_def(aoi_hit) > max_group_index:
                    do.write(" FIRST PASS END")
                    first_pass_end = 1
                if second_pass_start and not second_pass_end and int_def(aoi_hit) > max_group_index:
                    do.write(" SECOND PASS END")
                    second_pass_end = 1
                if last_fix_aoi in group and int_def(aoi_hit) > 0 and int_def(last_fix_aoi) > int_def(aoi_hit):
                    regressions_outof += 1
                    regressions_outof_tgt.append(aoi_hit)
            last_fix_aoi = aoi_hit
            do.write(" \n")
        total_skip = "FALSE" if first_pass_start else "TRUE"
        reread_duration = total_dwelltime - first_pass_duration
        regressions_into_src_packed = ','.join(map(str, regressions_into_src))
        regressions_outof_tgt_packed = ','.join(map(str, regressions_outof_tgt))
        mean_dwelltime_per_word = total_dwelltime / group_word_count
        mean_first_pass_dwelltime_per_word = first_pass_duration / group_word_count
        mean_reread_dwelltime_per_word = reread_duration / group_word_count
        do.write("Last AOI index: {}, Total dwell time: {:.1f}, Num fixations: {}\n".format(last_fix_aoi, total_dwelltime, num_fix))
        do.write("First fixation start: {}, First fixation duration: {}, First pass duration: {}, First pass fixations: {}\n".format(first_pass_start, first_fix_duration, first_pass_duration, first_pass_num_fix,))
        do.write("Second pass start: {}, Second pass duration: {}, Second pass fixations: {}, Total skip: {}\n".format(second_pass_start, second_pass_duration, second_pass_num_fix, total_skip))
        do.write("Num regressions into: {}, Sources regressions into: {}, Num regressions out of: {}, Targets regressions out of: {}\n\n".format(regressions_into, regressions_into_src_packed, regressions_outof, regressions_outof_tgt_packed))
        so.write("{}\t{}\t{}\t{:.1f}\t{:.1f}\t{}\t{:.1f}\t{}\t{:.1f}\t{:.1f}\t{}\t{:.1f}\t{:.1f}\t{}\t{:.1f}\t{:.1f}\t{}\t{:.1f}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(stimulus, ",".join(group), participant, total_dwelltime, mean_dwelltime_per_word, num_fix, first_pass_start, first_fix_duration, first_pass_duration, mean_first_pass_dwelltime_per_word, first_pass_num_fix, second_pass_start, second_pass_duration, second_pass_num_fix, reread_duration, mean_reread_dwelltime_per_word, total_skip, regressions_into, regressions_into_src_packed, regressions_outof, regressions_outof_tgt_packed, trial_num, trial_start, group_word_count,  group_char_count))
    print('done.')
print('All done.')
