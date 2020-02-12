
library(ggplot2)
library(plyr)
library(Rmisc)
library(gtools)
library(reshape2)
library(gtools)

data <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/conflicts_summary_0.csv")
data$id <- as.character(data$dataset)
data$num_id <- as.numeric(data$dataset)
data[with(data, order(num_id)), ]

datasets <- c(100, 500, 1000, 2500, 5000)
times <- c(5.83333, 17.5, 36.16667, 67.66667, 166.833336)

time <- data.frame(datasets, times)

feedback_100 <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/100_feedback_results.csv")
feedback_100$dataset <- 100
feedback_500 <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/500_feedback_results.csv")
feedback_500$dataset <- 500
feedback_1000 <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/1000_feedback_results.csv")
feedback_1000$dataset <- 1000
feedback_2000 <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/2000_feedback_results.csv")
feedback_2000$dataset <- 2000
feedback_5000 <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/5000_feedback_results.csv")
feedback_5000$dataset <- 5000

feedback <- rbind(feedback_100, feedback_500, feedback_1000, feedback_2000, feedback_5000)


feedback_0 <- feedback[feedback$id < 1,]
feedback_0_10 <- feedback[feedback$id < 10,]
feedback_10_20 <- feedback[feedback$id >= 10 & feedback$id < 20,]
feedback_20_30 <- feedback[feedback$id >= 20,]

feedback_0$ci <- 0
feedback_0$se <- 0
feedback_0$sd <- 0
feedback_0$N <- 1


temp_0_10 <- summarySE(feedback_0_10, measurevar="rsquared", groupvars=c("dataset"))
temp_0_10$id <- 10
temp_10_20 <- summarySE(feedback_10_20, measurevar="rsquared", groupvars=c("dataset"))
temp_10_20$id <- 20
temp_20_30 <- summarySE(feedback_20_30, measurevar="rsquared", groupvars=c("dataset"))
temp_20_30$id <- 30

result <- rbind(feedback_0, temp_0_10, temp_10_20, temp_20_30)

m <- ggplot(result, aes(x=id, y=rsquared, group=factor(dataset), fill=factor(dataset)))
m +
  geom_bar(aes(fill=factor(dataset)),position=position_dodge(), stat="identity") +
  #geom_errorbar(aes(ymin=rsquared-ci, ymax=rsquared+ci), colour="black", width=5, position=position_dodge(9)) +
  #geom_line() +
  scale_x_continuous(limits = c(-10,40), breaks=c(0,10,20,30)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  #geom_smooth(method='lm') +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  scale_fill_grey(start = 0.2, end = .6) +
  theme(axis.line.x = element_line(color = 'black'),
        axis.line.y = element_line(color = 'black'),
        legend.justification=c(0,1),
        legend.position=c(0,1),
        panel.border = element_blank(),
        legend.title=element_blank(),
        axis.text = element_text(size = 24),
        axis.title = element_text(size = 24),
        text = element_text(size = 24)) +
  labs(fill='Dataset Size', colour="Dataset Size") +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=20, face="bold"), legend.position="right", legend.title.align=0.5)


m <- ggplot(feedback_100, aes(x=id, y=rsquared))
m +
  geom_point(stat="identity") +
  #scale_x_continuous(limits = c(-10,120), breaks=c(10,50,100)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  geom_smooth(method='lm', colour="#666666") +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  ggtitle("Dataset #100") +
  scale_fill_grey(start = 0.3, end = .6) +
  theme(
        plot.title = element_text(hjust = 0.5),
        axis.line.x = element_line(color = 'black'),
        axis.line.y = element_line(color = 'black'),
        legend.justification=c(0,1),
        legend.position=c(0,1),
        panel.border = element_blank(),
        legend.title= element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 16),
        text = element_text(size = 16)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=10, face="bold"), legend.position="right", legend.title.align=0.5)



m <- ggplot(feedback_500, aes(x=id, y=rsquared))
m +
  geom_point(stat="identity") +
  #scale_x_continuous(limits = c(-10,120), breaks=c(10,50,100)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  geom_smooth(method='lm', colour="#666666") +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  ggtitle("Dataset #500") +
  scale_fill_grey(start = 0.3, end = .6) +
  theme(
    plot.title = element_text(hjust = 0.5),
    axis.line.x = element_line(color = 'black'),
    axis.line.y = element_line(color = 'black'),
    legend.justification=c(0,1),
    legend.position=c(0,1),
    panel.border = element_blank(),
    legend.title= element_blank(),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 16),
    text = element_text(size = 16)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=10, face="bold"), legend.position="right", legend.title.align=0.5)




m <- ggplot(feedback_1000, aes(x=id, y=rsquared))
m +
  geom_point(stat="identity") +
  #scale_x_continuous(limits = c(-10,120), breaks=c(10,50,100)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  geom_smooth(method='lm', colour="#666666") +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  ggtitle("Dataset #1000") +
  scale_fill_grey(start = 0.3, end = .6) +
  theme(
    plot.title = element_text(hjust = 0.5),
    axis.line.x = element_line(color = 'black'),
    axis.line.y = element_line(color = 'black'),
    legend.justification=c(0,1),
    legend.position=c(0,1),
    panel.border = element_blank(),
    legend.title= element_blank(),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 16),
    text = element_text(size = 16)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=10, face="bold"), legend.position="right", legend.title.align=0.5)

m <- ggplot(feedback_2000, aes(x=id, y=rsquared))
m +
  geom_point(stat="identity") +
  geom_line(stat="identity") +
  #scale_x_continuous(limits = c(-10,120), breaks=c(10,50,100)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  #geom_smooth(method='lm', colour="#666666") +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  ggtitle("Dataset #2000") +
  scale_fill_grey(start = 0.3, end = .6) +
  theme(
    plot.title = element_text(hjust = 0.5),
    axis.line.x = element_line(color = 'black'),
    axis.line.y = element_line(color = 'black'),
    legend.justification=c(0,1),
    legend.position=c(0,1),
    panel.border = element_blank(),
    legend.title= element_blank(),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 16),
    text = element_text(size = 16)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=10, face="bold"), legend.position="right", legend.title.align=0.5)


m <- ggplot(feedback_5000, aes(x=id, y=rsquared))
m +
  geom_point(stat="identity") +
  #scale_x_continuous(limits = c(-10,120), breaks=c(10,50,100)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  geom_smooth(method='lm', colour="#666666") +
  xlab("# of Feedbacks") +ylab("R-squared") +
  theme_bw() +
  ggtitle("Dataset #5000") +
  scale_fill_grey(start = 0.3, end = .6) +
  theme(
    plot.title = element_text(hjust = 0.5),
    axis.line.x = element_line(color = 'black'),
    axis.line.y = element_line(color = 'black'),
    legend.justification=c(0,1),
    legend.position=c(0,1),
    panel.border = element_blank(),
    legend.title= element_blank(),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 16),
    text = element_text(size = 16)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=10, face="bold"), legend.position="right", legend.title.align=0.5)


data_table <- table(data$num_id)
data_levels <- names(data_table)[order(data_table)]
data$lid <- factor(data$id, levels = data_levels)
m <- ggplot(data, aes(x=lid, y=precision, group = 1))
m +
  #geom_point(stat="identity") +
  #geom_line(stat="identity") +
  #geom_errorbar(aes(ymin=confidence_bottom, ymax=confidence_top), colour="black", width=0.1, position=position_dodge(35)) +
  #scale_x_continuous(limits = c(-100,6000), breaks=c(100,500,1000,2000, 5000)) +
  #scale_y_continuous(limits = c(0,0.4), breaks=seq(0,0.4,by=0.10)) +
  xlab("Dataset Size") + ylab("Precision") +
  #theme_bw() +
  theme(axis.line.x = element_line(color = 'black'),
        axis.line.y = element_line(color = 'black'),
        legend.justification=c(0,1),
        legend.position=c(0,1),
        panel.border = element_blank(),
        legend.title=element_blank(),
        axis.text = element_text(size = 30),
        axis.title = element_text(size = 30),
        text = element_text(size = 30)) +
  theme(panel.grid.major = element_line("black", size = 0.02), panel.grid.minor = element_line("black", size = 0.1),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=28, face="bold"), legend.position="right", legend.title.align=0.5)




m <- ggplot(time, aes(x=datasets, y=times))
m +
  geom_line(stat="identity") +
  geom_point(stat="identity") +
  #geom_errorbar(aes(ymin=rsquared-ci, ymax=rsquared+ci), colour="black", width=5, position=position_dodge(9)) +
  #geom_line() +
  #scale_x_continuous(limits = c(0,5000), breaks=c(0,500,1000,2000,5000)) +
  scale_y_continuous(limits = c(0,max(times)+10), breaks=seq(0,max(times)+20,by=20)) +
  #geom_smooth(method='lm') +
  xlab("Dataset Size") +ylab("Training Time (m)") +
  scale_fill_grey(start = 0.2, end = .6) +
  theme(axis.line.x = element_line(color = 'black'),
        axis.line.y = element_line(color = 'black'),
        legend.justification=c(0,1),
        legend.position=c(0,1),
        panel.border = element_blank(),
        legend.title=element_blank(),
        axis.text = element_text(size = 30),
        axis.title = element_text(size = 30),
        text = element_text(size = 30)) +
  labs(fill='Dataset Size', colour="Dataset Size") +
  theme(panel.grid.major = element_line("black", size = 0.02), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black")) +
  theme(legend.title = element_text(colour="black", size=28, face="bold"), legend.position="right", legend.title.align=0.5)
