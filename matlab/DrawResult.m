function [  ] = DrawResult( tripR, tripN, centreP)
hold on
plotXY = zeros(2,tripN);
for i = 1:tripN
    plotXY(i,1) = centreP(tripR(i),2); 
    plotXY(i,2) = centreP(tripR(i),1); 
end

plot(plotXY(:,1),plotXY(:,2),':>b','LineWidth',2);
hold on

for i = 1:tripN
    
    plot(centreP(tripR(i),2),centreP(tripR(i),1),'bx','MarkerSize',5,'LineWidth',2);
    hold on
    str = num2str(i);
    text(centreP(tripR(i),2),centreP(tripR(i),1),str,'FontSize', 20)
end
end

