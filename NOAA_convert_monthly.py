'''
Author: Liam Haining

Takes a csv file name as a command line argument
Assumes format of STATION,NAME,LATITUDE,LONGITUDE,ELEVATION,DATE,PRCP,PRCP_ATTRIBUTES,TAVG,TAVG_ATTRIBUTES
Filters data by Latitude/Longitude and returns in a new csv
'''

import sys


# Determines if a coordinate is contained by the limpopo region
def contained(lat, long):
    if long > 26.395269 and long < 31.844487 and lat > -25.368371 and lat < -22.133315:
        return True
    return False


def smart_split(s):
    a = 0
    result = []
    b = 1
    while b < len(s) and s[b] != '\n':
        if s[b] == ',' or s[b] == '\n' or b >= len(s):
            result.append(s[a:b])
            a = b+1
        if s[b] == '"' and s.find('"', b+1) != -1:
            b = s.find('"', b+1)
        b += 1
    result.append(s[a:b])
    return result


# Takes a csv filename and returns a string containing the filtered csv
def scrape_file(filename):
    f = open(filename)

    _list = smart_split(f.readline())
    result = ",".join(_list) + '\n'    # Keep the header in the result
    line = f.readline() # Get first set of data
    # Keep track of success rates
    fail_count = 0
    total = 0
    _contained = 0
    cur_station = None
    cur_month = None
    cur_year = None
    prev_line = None
    total_temp = 0
    total_prcp = 0
    total_days = 0


    while line:
        total += 1
        try:
            data = smart_split(line)
            station = data[0]
            month, _, year = data[5].split('/')
            if contained(float(data[2]), float(data[3])):
                if cur_station == None or (cur_station == station and cur_month == month and cur_year == year):
                    if cur_station == None:
                        cur_station = station
                        cur_month = month
                        cur_year = year
                        prev_line = line
                    if (data[6] != ''):
                        total_prcp += float(data[6])
                    if (data[7] != ''):
                        total_temp += float(data[7])
                        total_days += 1

                    _contained += 1
                    line = f.readline()
                else:
                    # Appending monthly data to result csv
                    data = smart_split(prev_line)   # Reusing constant data such as station name
                    # Modify temperature, precipitation, and date
                    data[7] = str(round(total_temp / total_days))
                    data[6] = str(round(total_prcp, 2))
                    data[5] = cur_year + ('0'*(2-len(cur_month)) + cur_month) + '00'
                    new_line = ','.join(data)
                    new_line += '\n'
                    result += new_line
                    # Reset counters
                    cur_station = None
                    cur_month = None
                    cur_year = None
                    prev_line = None
                    total_temp = 0
                    total_prcp = 0
                    total_days = 0
                    # Correct total
                    total -= 1

        except (ValueError) as e:
            print('Could not parse """' + line + '"""')
            fail_count += 1
            line = f.readline()
    # Report success rate
    print("Successfully read " + str(total - fail_count) + " out of " + str(total) + " lines")
    print(str(_contained) + " out of " + str(total - fail_count) + " points were contained by the limpopo region")
    return result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Invalid Command Line Argument Count")
    else:
        filename = sys.argv[1]
        if filename[-4:] != '.csv':
            print("Invalid file type, must be a csv")
        else:
            contents = scrape_file(filename)
            f = open(filename[:-4] + '_monthly.csv', 'w')
            f.write(contents)
            f.close()

