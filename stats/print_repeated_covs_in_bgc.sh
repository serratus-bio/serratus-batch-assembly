eFalserep CoV ~/serratus-assemblies-CoV_id95-60_reads100p_score30p.unique/*.txt | awk -F: '{print $1}' |  awk '{a[$0]++}END{for(i in a){if(a[i] > 2){print i}}}'
