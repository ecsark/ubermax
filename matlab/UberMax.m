close all

%clear 
clc

s = 4;
DesireTime = 4*60*60;
time_buff = 0.01;
startP = 22;
endP = 24;
startTime = 11*60*60+11*60+11;

maxEarn = 0;
maxExp = 0;
maxRoutine = [];
maxRoutineE = [];

if s <1
    tic
    delete(gcp('nocreate'))
    rng default; % For reproducibility
    pool = parpool;                      % Invokes workers
    stream = RandStream('mlfg6331_64');  % Random number stream
    options = statset('UseParallel',1,'UseSubstreams',1,'Streams',stream);

    
    RawDataY = csvread('rawDataY.csv');
    RawDataG = csvread('rawDataG.csv');
    RawData = [RawDataY;RawDataG];
    % RawData = RawData(1:500,:);
    [totalN,~] = size(RawData);

    clusterN =33;
    
%     timeLookUp = 12;
%     pickTimeZinfo = RawData( RawData(:,1) == timeLookUp , 4:5);
%     RawData = pickTimeZinfo;

    [datalength,~] = size(RawData);
    tripZone = zeros(datalength,2); % stZ,edZ,stT,period, dist
    
    opts = statset('Display','final');
    tryN = 1;
    [tripZone(:,1),Center] = kmeans(RawData(:,4:5),clusterN,'Distance','cityblock',...
    'Replicates',tryN,'Options',opts);

    for m = 1:datalength
        tripZone(m,2) = 1;
        min_dist = (RawData(m,6) - Center(1,1))^2 + (RawData(m,7) - Center(1,2))^2;
        for i = 2:clusterN
            cur_dist = (RawData(m,6) - Center(i,1))^2 + (RawData(m,7) - Center(i,2))^2;
            if cur_dist < min_dist
                tripZone(m,2) = i;
                min_dist = cur_dist;
            end
        end
    end
end
if s < 2
    cluster_info = zeros(24,clusterN,clusterN,3);
    sumOut=zeros(24,1);
    ZonesumOut=zeros(24,clusterN,1);
    for m = 1:datalength
        cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),1)=cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),1)+RawData(m,2);
        cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),2)=cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),2)+RawData(m,3);
        cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),3)=cluster_info(RawData(m,1),tripZone(m,1),tripZone(m,2),3)+ 1;
        ZonesumOut(RawData(m,1),tripZone(m,1))=ZonesumOut(RawData(m,1),tripZone(m,1)) +1;
        sumOut(RawData(m,1)) = sumOut(RawData(m,1))+1;
    end
    
    for t = 1:24
        for c = 1:clusterN
            for r = 1:clusterN
                cluster_info(t,c,r,1) = cluster_info(t,c,r,1) / cluster_info(t,c,r,3);
                cluster_info(t,c,r,2) = cluster_info(t,c,r,2) / cluster_info(t,c,r,3);
                if cluster_info(t,c,r,3) == 0 || cluster_info(t,c,r,1) == 0 
                    cluster_info(t,c,r,1) = 0;
                    cluster_info(t,c,r,2) = 0;
                end
            end
        end
    end  
    
	toc
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% clustering done
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if s<3
    figure(1)
    writerObj = VideoWriter('NYC_tMap_Hours.avi');
    open(writerObj);
    filename = 'NYC_tMap_Hours.gif';

    timeHP = max(ZonesumOut(t,:));
    for t=1:24
        clf
        timeHP = max(ZonesumOut(t,:));
        for i = 1:clusterN
            locH = ZonesumOut(t,i);
            if locH <= timeHP/2
                r =1;
                g = 2*locH/timeHP;
            else
                g =1;
                r =2-2*locH/timeHP;
            end
            xy = [RawData(tripZone(:,1)==i ,4),RawData(tripZone(:,1)==i,5)];
            plot(xy(:,2),xy(:,1),'.','MarkerSize',12,'Color',[g r 0]);
            axis([ -74.1 -73.7 40.55 40.95])
            hold on
        end

        title (['Taxi Distribution in NYC @ ',num2str(t),' H']);
        grid
        grid minor
        axis equal
        axis([ -74.1 -73.7 40.55 40.95])
        xlabel('longitude')
        ylabel('latitude')    
        frame = getframe(1);
        for rpt = 1:5
            writeVideo(writerObj,frame);
        end
        im = frame2im(frame);
        [imind,cm] = rgb2ind(im,256);
        if t == 1;
            imwrite(imind,cm,filename,'gif', 'Loopcount',inf);
        else
            for rpt = 1:5
                imwrite(imind,cm,filename,'gif','WriteMode','append');
            end
        end
        pause (0.1);
    end
    close(writerObj);

    figure(2)
    for i = 1:clusterN
        xy = [RawData(tripZone(:,1)==i ,4),RawData(tripZone(:,1)==i,5)];
        plot(xy(:,2),xy(:,1),'.','MarkerSize',12);
        axis([ -74.1 -73.7 40.55 40.95])
        hold on
    end
    title 'Taxi Distribution in NYC'
    grid
    grid minor
    axis equal
    axis([ -74.1 -73.7 40.55 40.95])
    xlabel('longitude')
    ylabel('latitude')

    savefig('NYC_tMap.fig')    
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Maping done
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



[~,~,timeNeed] = GainT([startP,endP],sumOut,cluster_info,startTime);

if timeNeed > DesireTime
    maxRoutine = 0
else
    tic

    for nextP1  = 1:clusterN
        for nextP2  = 0:clusterN
            for nextP3 = 0:clusterN
                for nextP4 = 0:clusterN
                    for nextP5 = 0:clusterN
                        tripR = [startP,nextP1,nextP2,nextP3,nextP4,nextP5];
                        [earnExp,earnM,earnT,lastTrip,~] = GainT(tripR,sumOut,cluster_info,startTime);
                        if lastTrip == endP && (DesireTime -earnT)>-DesireTime*time_buff
                            if maxEarn < earnM
                                maxEarn = earnM;
                                maxRoutine = tripR;
                            end
                            if maxExp < earnExp
                                maxExp = earnExp;
                                maxRoutineE = tripR;
                            end
                        end
                    end 
                end  
            end
        end
    end


    maxRoutine
    [~,maxRoutine_M,maxRoutine_T,~,tripN] = GainT(maxRoutine,sumOut,cluster_info,startTime)
    
    openfig('NYC_tMap.fig');
    DrawResult( maxRoutine, tripN, Center)
    str1 = sprintf('Revenue = %f',maxRoutine_M);
    str2 = ['Time = ',secs2hms(maxRoutine_T)];
    legend(str1,str2,'Location','southeast')
    
    % maxRoutineE
    % [~,maxRoutineE_M,maxRoutineE_T] = GainT(maxRoutineE,sumOut,cluster_info)


    if (maxRoutineE(3)==maxRoutineE(4) && maxRoutineE(4)==maxRoutineE(5)) ...
            || (maxRoutineE(3)==maxRoutineE(4) && maxRoutineE(3)==maxRoutineE(2)) ...
            && maxRoutineE(3)~=0
        [~,~,earnT] = GainT(maxRoutineE,sumOut,cluster_info,startTime);
        [~,~,timeSeq] = GainT([maxRoutineE(3),maxRoutineE(4),0,0,0],sumOut,cluster_info,startTime);
        while((DesireTime - earnT-timeSeq)>-DesireTime*time_buff)
            maxRoutineE = [maxRoutineE(1:3) maxRoutineE(3) maxRoutineE(4:end)];
            [earnExp,earnM,earnT,lastTrip] = GainT(maxRoutineE,sumOut,cluster_info,startTime);
        end
    end
    maxRoutineE
    [~,maxRoutineE_M,maxRoutineE_T,~,tripNE] = GainT(maxRoutineE,sumOut,cluster_info,startTime)
    
    openfig('NYC_tMap.fig');
    DrawResult( maxRoutineE, tripNE, Center)
    str1 = sprintf('Revenue = %f',maxRoutineE_M);
    str2 = ['Time =',secs2hms(maxRoutineE_T)];
    legend(str1,str2,'Location','southeast')
    
    toc
end

