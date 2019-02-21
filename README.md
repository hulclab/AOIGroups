# AOIGroups
Scripts for calculating statistical data for word-aoi-groups.  
These scripts were created to facilitate analysis of multi-word AOI groups in linguistic eyetracking data.  
SMI beGaze automatically generates AOIs around each word of a text stimulus. Our researchers needed a tool to perform multiple pass analysis, regression analysis etc. for variable groupings of these AOIs. Later a variant of the script that works with exported data from Tobii Studio was added.

## Usage
The two scripts are meant to be used as command-line tools. You can simply download the executables in the [dist](tree/master/dist) directory, which were generated using pyinstaller on a windows system running Python 3.7, or, if you want to run the scripts on other systems or if you need to modify the scripts for your own purposes, download the sources. They should run on a standard [Python](https://www.python.org/downloads/) 3.7 installation.

### smi_aoi_group
```
smi_aoi_group.exe SOURCE
```
Source file is expected to be a _SMI BeGaze_ export file (Metrics export - Event statistics - single), where each line represents a fixation event including word AOI information.  
First execution of the tool creates a `SOURCE.list` file containing all AOIs in the data file, grouped by stimulus, like this: 
```
Critical_T1_C1a, 1, José
Critical_T1_C1a, 2, y
Critical_T1_C1a, 3, Andrés
Critical_T1_C1a, 4, comen
Critical_T1_C1a, 5, muchos
Critical_T1_C1a, 6, dulces.
Critical_T1_C1a, 7, A
Critical_T1_C1a, 8, pesar
Critical_T1_C1a, 9, de
Critical_T1_C1a, 10, ello,
Critical_T1_C1a, 11, están
Critical_T1_C1a, 12, delgados.
```
To calculate group metrics, create a file named `SOURCE.groups`. Define your groups using the AOI indices listed in the `SOURCE.list` file, e.g. to analyze the sentence fragment _"A pesar de ello,"_ from the example above, the `SOURCE.groups` file should look like this: 
```
Critical_T1_C1a 7,8,9,10
``` 
You can enter multiple lines in one `SOURCE.groups` file, which will be processed consecutively.  
On second execution (if a valid `SOURCE.groups` file is present), the tool generates a `SOURCE.stats` file like this: 
```
Stimulus	AOI group	Participant	Total dwell time	Mean dwelltime per word	Total num fixation	First fixation start	First fixation duration	First pass duration	First pass mean dwelltime per word	First pass num fixations	Second pass start	Second pass durations	Second pass num fixations	Re-readings duration	Total Skip	Num regressions into	Sources regressions into	Num regressions out of	Targets regressions out of	Trial no.	Trial start time	Group word count	Group char count
Critical_T1_C1a	7,8,9,10	EXP_01_P_01	356.2	89.1	3	1216.0	134.0	356.2	89.1	3	0.0	0.0	0	0.0	0.0	FALSE	0.0		0		2	27036112.4	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_02	1129.1	282.3	6	6763.7	352.1	880.9	220.2	4	12658.1	118.1	1	248.2	62.1	FALSE	2.0	18,15	0		4	1721543.4	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_03	386.2	96.6	4	1274.5	70.0	386.2	96.6	4	0.0	0.0	0	0.0	0.0	FALSE	1.0	8	0		11	2425390.3	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_04	126.1	31.5	1	1403.4	126.1	126.1	31.5	1	0.0	0.0	0	0.0	0.0	FALSE	0.0		0		15	902713.3	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_06	700.1	175.0	4	1808.1	320.1	320.1	80.0	1	4055.2	222.0	2	380.0	95.0	FALSE	2.0	18,18	0		4	2565602.6	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_07	448.2	112.0	4	1873.7	190.1	448.2	112.0	4	0.0	0.0	0	0.0	0.0	FALSE	0.0		0		2	4545946.0	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_08	250.0	62.5	2	2443.8	104.0	250.0	62.5	2	0.0	0.0	0	0.0	0.0	FALSE	0.0		0		4	1799017.6	4	12
Critical_T1_C1a	7,8,9,10	EXP_01_P_09	334.0	83.5	4	1421.1	66.0	280.0	70.0	3	3107.9	54.0	1	54.0	13.5	FALSE	2.0	9,14	0		19	3867765.5	4	12
...
```
Additionally, a `SOURCE.debug` file is created with detailed information on the AOI matching and calculations, which can be consulted in case the stats file contains unplausible results: 
```
Stimulus Critical_T1_C1a Participant EXP_01_P_01 Trial no. 2 Trial start time 27036112.4 Group ['7', '8', '9', '10'] A pesar de ello  Group word count 4 Group char count 12 
Fix   1:	                      José	    1	    1.5	   164.1 
Fix   2:	                      José	    1	  193.5	   122.0 
Fix   3:	                    Andrés	    3	  357.7	   126.4 
Fix   4:	                     comen	    4	  515.7	   182.1 
Fix   5:	                    muchos	    5	  743.8	   160.1 
Fix   6:	                   dulces.	    6	  941.9	   240.1 
Fix   7:	                         A	    7	 1216.0	   134.0 <- 
Fix   8:	                     pesar	    8	 1376.0	   132.1 <- 
Fix   9:	                     ello,	   10	 1612.1	    90.1 <- 
Fix  10:	                     están	   11	 1740.2	   162.0 FIRST PASS END 
Fix  11:	                 delgados.	   12	 1942.2	   220.1 
Fix  12:	                       Les	   13	 2202.3	    78.1 
Fix  13:	                       Les	   13	 2312.4	    96.0 
Fix  14:	                     gusta	   14	 2512.5	   122.3 
Fix  15:	                     gusta	   14	 2660.5	   154.1 
Fix  16:	                     mucho	   15	 2864.6	   124.0 
Fix  17:	                       ver	   16	 3028.7	   306.1 
Fix  18:	                       ver	   16	 3346.8	    66.0 
Fix  19:	                       ver	   16	 3430.9	   198.1 
Fix  20:	                       ver	   16	 3665.7	   285.3 
Fix  21:	               televisión.	   18	 3989.0	   174.1 
Last AOI index: 18, Total dwell time: 356.2, Num fixations: 3
...
Stimulus Critical_T1_C1a Participant EXP_01_P_06 Trial no. 4 Trial start time 2565602.6 Group ['7', '8', '9', '10'] A pesar de ello  Group word count 4 Group char count 12 
Fix   1:	                      José	    1	    1.9	   101.4 
Fix   2:	                    Andrés	    3	  197.4	   152.1 
Fix   3:	                     comen	    4	  425.5	   102.0 
Fix   4:	                    muchos	    5	  701.6	   194.1 
Fix   5:	                     comen	    4	  963.8	   232.1 
Fix   6:	                   dulces.	    6	 1243.9	   176.1 
Fix   7:	                   dulces.	    6	 1624.0	   148.1 
Fix   8:	                     pesar	    8	 1808.1	   320.1 <- 
Fix   9:	                     están	   11	 2180.4	   182.0 FIRST PASS END 
Fix  10:	                 delgados.	   12	 2402.4	   198.1 
Fix  11:	                 delgados.	   12	 2790.6	   358.1 
Fix  12:	                     mucho	   15	 3368.8	   106.0 
Fix  13:	                     gusta	   14	 3520.9	   104.0 
Fix  14:	                       ver	   16	 3669.0	   114.1 
Fix  15:	               televisión.	   18	 3851.1	   160.0 
Fix  16:	                         A	    7	 4055.2	   128.0 <- 
Fix  17:	                   dulces.	    6	 4279.2	   354.3 
Fix  18:	                     pesar	    8	 4677.4	    94.0 <- 
Fix  19:	                        la	   17	 4955.5	   196.1 SECOND PASS END 
Fix  20:	               televisión.	   18	 5179.7	   214.2 
Fix  21:	                     pesar	    8	 5421.8	   158.0 <- 
Last AOI index: 8, Total dwell time: 700.1, Num fixations: 4
...
``` 
### tobii-aoi-group

## Authors

* **Takara Baumbach** ([takb](https://github.com/takb))

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
