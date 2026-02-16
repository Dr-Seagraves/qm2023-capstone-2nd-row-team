#!/bin/bash

# Build POST data for all demographics
POST_DATA="alldemos=on"
POST_DATA="${POST_DATA}&freq=month"
POST_DATA="${POST_DATA}&start_year=1978"
POST_DATA="${POST_DATA}&end_year=2025"
POST_DATA="${POST_DATA}&scores=rel"

# Add all demographic groups manually
# Age groups
POST_DATA="${POST_DATA}&age_18=on&age_35=on&age_45=on&age_55=on&age_65=on"
# Regions
POST_DATA="${POST_DATA}&region_1=on&region_2=on&region_3=on&region_4=on"
# Sex
POST_DATA="${POST_DATA}&sex_1=on&sex_2=on"
# Education
POST_DATA="${POST_DATA}&ehs=on&esc=on&ecd=on&egs=on"
# Income groups
POST_DATA="${POST_DATA}&inc_1=on&inc_2=on&inc_3=on&inc_4=on&inc_5=on"
# All households
POST_DATA="${POST_DATA}&all=on"

# Add all variables
VARIABLES="bago bexp btrd bus12 bus5 dur durrn gas1px gas5px govt hmv hom hompx1 hompx5 homrn homval icc ice ics inex inv news newsrn pago pago5 pagorn pcry pexp pexp5 pinc pinc2 pjob pssa pstk ptrd ptrd5 px1 px5 ratex rinc shom shomrn umex veh vehrn"

for var in $VARIABLES; do
  POST_DATA="${POST_DATA}&${var}=on"
done

# Download the CSV file
curl -s -X POST \
  -d "$POST_DATA" \
  https://data.sca.isr.umich.edu/subset/output.php \
  -o "$(dirname "$0")/SCA_data.csv"

echo "Download complete. File saved to $(dirname "$0")/SCA_data.csv"
ls -lh "$(dirname "$0")/SCA_data.csv"
