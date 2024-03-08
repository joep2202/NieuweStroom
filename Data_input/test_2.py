

class test:
    def __init__(self, data):
        self.data = data

    def interval_to_time(self, interval):
        hours = interval // 4  # Each interval represents 15 minutes, so 4 intervals = 1 hour
        minutes = (interval % 4) * 15  # Remaining intervals represent minutes
        return f"{hours:02d}:{minutes:02d}"

    def get_data(self, date, current_interval, length_forecast):
        print(date,current_interval,length_forecast)
        time = self.interval_to_time(current_interval)
        print(time, date+' ' + time)
        self.start = self.data[self.data['datum'].str.contains(date) & self.data['periode_van'].str.contains(time)]
        self.start_int = self.start.index[0]
        print(self.start_int)
        self.data = self.data.iloc[self.start_int:self.start_int+length_forecast]
        print(self.data)

