function [earnExp,earnM,earnT,lastTrip,tripN] = GainT(tripR,sumOut,trip_info,startTime)
fare_model = [3.0, 0.4, 2.15];
earnExp = 0;
earnM = 0;
earnT = 0;
lastTrip = 0;
[~,tripN ]= size(tripR);

for c = 1:(tripN-1)
    if tripR(c+1) > 0
        time_Z = floor(startTime/3600)+1;
        earnT = earnT + trip_info(time_Z,tripR(c),tripR(c+1),1) ;
        startTime = startTime+earnT;
        if startTime > 24*60*60
            startTime = startTime - 24*60*60;
        end
        oneTimeEarn = fare_model(1)+fare_model(2)*trip_info(time_Z,tripR(c),tripR(c+1),1) /60 + ...
                                    fare_model(3)*trip_info(time_Z,tripR(c),tripR(c+1),2);
        earnExp = earnExp+oneTimeEarn * ((trip_info(time_Z,tripR(c),tripR(c+1),3))/sumOut(time_Z));
        earnM = earnM + oneTimeEarn;
        
        lastTrip = tripR(c+1);
        tripN = c+1;
    else
        lastTrip = tripR(c);
        tripN = c;
        return
    end
end

end

