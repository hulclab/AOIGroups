#!/usr/bin/python3
# pack: pyinstaller --onefile tobii_aoi_group.py

import sys
import os
import re
import argparse
from collections import defaultdict


def hash3d():
    return defaultdict(dict)

def int_def(value):
    try:
        return int(value)
    except:
        return 0

parser = argparse.ArgumentParser(description='Process tobii export data.', argument_default=argparse.SUPPRESS)
parser.add_argument('source', help='input file name')
parser.add_argument('--cols', '-c', help='number of fixed cols for aoi detection', default=24)
parser.add_argument('--nonames', '-n', action='store_false', help='switch to no named aois mode (old behavior)', default=True)
args = parser.parse_args()

source = args.source
fullsource = source+".full"
groupssource = source+".groups"
statsoutfile = source+".stats"
debugoutfile = source+".debug"

if not os.path.isfile(source) or os.path.getsize(source) == 0:
    sys.exit("Could not read data file or no content: %s" % source);
if not os.path.isfile(fullsource) or os.path.getsize(fullsource) == 0:
    sys.exit("Could not read full data file or no content: %s" % fullsource);
if not os.path.isfile(groupssource) or os.path.getsize(groupssource) == 0:
    sys.exit("Could not read group data file or no content: %s" % groupssource);

print('Processing full data file...')
subject = re.compile(r"ImageStart")
res = {}
for l in open(fullsource):
    sm = subject.search(l)
    if sm:
        data = l.split("\t")
        res[(data[1], data[3])] = data[4]
#print (res)

print('Processing data file...')
infile = open(source)
header = infile.readline().split("\t")
data = defaultdict(hash3d)
trial = hash3d()
aoi_names = hash3d()
fix_cols = args.cols
replace = re.compile(r".*\[(.*)\].*")
if (args.nonames):
    for l in infile:
        cols = l.split("\t")
        fix_start = str(int(cols[4]) - int(res[(cols[1], cols[3])]))
        fix_aoi = "-"
        current_aoi_index = 1
        for index in range(fix_cols, len(cols) -1):
            if cols[index] == "1":
                fix_aoi = replace.sub(r'\1', header[index])
                break
            if (cols[index] == '0'):
                current_aoi_index += 1
        if fix_aoi == "-":
            current_aoi_index = "-"
        data[cols[3]][cols[1]][int(cols[21])] = (int(fix_start), int(cols[23]), str(current_aoi_index))
        trial[cols[3]][cols[1]] = res[(cols[1], cols[3])]
        aoi_names[cols[3]][current_aoi_index] = fix_aoi
        aoi_names[cols[3]][0] = "-"
else:
    for l in infile:
        cols = l.split("\t")
        fix_start = str(int(cols[4]) - int(res[(cols[1], cols[3])]))
        fix_aoi = "-"
        for index in range(fix_cols, len(cols) -1):
            if cols [index] == "1":
                fix_aoi = replace.sub(r'\1', header[index])
        data[cols[3]][cols[1]][int(cols[21])] = (int(fix_start), int(cols[23]), fix_aoi)
        trial[cols[3]][cols[1]] = res[(cols[1], cols[3])]
#print (data)

print('Processing groups...')
do = open(debugoutfile, 'w')
so = open(statsoutfile, 'w')
so.write("Stimulus\tAOI group\tParticipant\tTotal dwell time\tTotal num fixation\tFirst fixation start\tFirst fixation duration\tFirst pass duration\tFirst pass num fixations\tSecond pass start\tSecond pass durations\tSecond pass num fixations\tRe-readings duration\tTotal Skip\tNum regressions into\tSources regressions into\tNum regressions out of\tTargets regressions out of\tTrial start time\tGroup word count\tGroup char count\n")
for line in open(groupssource):
    group = re.split(r"[\t,]", line.strip())
    stimulus = group.pop(0)
    max_group_index = int(max(group, key=int))
    group_word_count = len(group)
    group_char_count = 0
    group_str = ""
    if (args.nonames):
        for aoi in group:
            group_char_count += len(re.sub(r'\d', '', aoi_names[stimulus][int_def(aoi)]))
            group_str += aoi_names[stimulus][int_def(aoi)] + " "
    print("Processing %s... " % stimulus, end="");
    for participant, part_data in data[stimulus].items():
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
        do.write("Stimulus {} Participant {} Trial start time {} Group {} {} Group word count {} Group char count {} \n".format(stimulus, participant, res[(participant, stimulus)], group, group_str, group_word_count, group_char_count))
        for fixation, fix_data in part_data.items():
            (start, duration, aoi_hit) = fix_data
            if (args.nonames):
                do.write("Fix {:>3}:\t {:>25}\t {:>4}\t{:>5}\t{:>8}".format(fixation, aoi_names[stimulus][int_def(aoi_hit)], aoi_hit, start, duration))
            else:
                do.write("Fix {:>3}:\t {:>4}\t{:>5}\t{:>8}".format(fixation, aoi_hit, start, duration))
            if aoi_hit in group:
                do.write(" <-")
                num_fix += 1
                total_dwelltime += duration;
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
                    regressions_outof+= 1
                    regressions_outof_tgt.append(aoi_hit);
            last_fix_aoi = aoi_hit;
            do.write(" \n")
        total_skip = "FALSE" if first_pass_start else "TRUE"
        reread_duration = total_dwelltime - first_pass_duration
        regressions_into_src_packed = ','.join(regressions_into_src)
        regressions_outof_tgt_packed = ','.join(regressions_outof_tgt)
        do.write("Last AOI index: {}, Total dwell time: {}, Num fixations: {}\n".format(last_fix_aoi, total_dwelltime, num_fix))
        do.write("First fixation start: {}, First fixation duration: {}, First pass duration: {}, First pass fixations: {}\n".format(first_pass_start, first_fix_duration, first_pass_duration, first_pass_num_fix,))
        do.write("Second pass start: {}, Second pass duration: {}, Second pass fixations: {}, Total skip: {}\n".format(second_pass_start, second_pass_duration, second_pass_num_fix, total_skip))
        do.write("Num regressions into: {}, Sources regressions into: {}, Num regressions out of: {}, Targets regressions out of: {}\n\n".format(regressions_into, regressions_into_src_packed, regressions_outof, regressions_outof_tgt_packed))
        so.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(stimulus, ",".join(group), participant, total_dwelltime, num_fix, first_pass_start, first_fix_duration,first_pass_duration, first_pass_num_fix, second_pass_start, second_pass_duration, second_pass_num_fix, reread_duration, total_skip, regressions_into, regressions_into_src_packed, regressions_outof, regressions_outof_tgt_packed, res[(participant, stimulus)], group_word_count, group_char_count))
    print('done.')
print('All done.')
