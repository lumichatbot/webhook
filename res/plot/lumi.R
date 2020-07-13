
library(ggplot2)
library(plyr)
library(Rmisc)
library(gtools)
library(reshape2)
library(precrec)
library(caret)

data <- read.csv("/home/asjacobs/workspace/webhook/res/results/conflicts_summary_0.csv")
data$id <- as.character(data$dataset)
data$num_id <- as.numeric(data$dataset)
data[with(data, order(num_id)), ]


datasets <- c(100, 500, 1000, 2500, 5000)

data_table <- table(data$num_id)
data_levels <- names(data_table)[order(data_table)]
data$lid <- factor(data$id, levels = data_levels)


time = ddply(data, c("model", "lid"), summarise,
                  N    = length(fit_time),
                  mean = mean(fit_time)
)



precision = ddply(data, c("model", "lid"), summarise,
              N    = length(precision),
              mean = mean(precision),
              sd   = sd(precision),
              se   = qt(0.975, df=N) * sd/sqrt(N)
)




recall = ddply(data, c("model", "lid"), summarise,
               N    = length(recall),
               mean = mean(recall),
               sd   = sd(recall),
               se   = qt(0.975, df=N) * sd/sqrt(N)
)

f1 = ddply(data, c("model", "lid"), summarise,
           N    = length(f1),
           mean = mean(f1),
           sd   = sd(f1),
           se   = qt(0.975, df=N) * sd/sqrt(N)
)

m <- ggplot(precision, aes(x=lid, y=mean, fill=model))
m +
  geom_bar(stat='identity', position='dodge') +
  #geom_point(stat="identity") +
  #geom_line(stat="identity") +
  geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(-100,6000), breaks=c(100,500,1000,2000, 5000)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  xlab("Dataset Size") + ylab("Precision") +
  scale_fill_manual("Model", values = c("svm" = "#505a5b", "log" = "#8f91a2", "forest" = "#343f3e"), labels = c("SVM", "LogReg", "Forest")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_line("#343f3e", size = 0.02),
        panel.grid.minor = element_line("#343f3e", size = 0.1),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position="right",
        legend.title.align=0.5)


recall = ddply(data, c("model", "lid"), summarise,
                  N    = length(recall),
                  mean = mean(recall),
                  sd   = sd(recall),
                  se   = qt(0.975, df=N) * sd/sqrt(N)
)

m <- ggplot(recall, aes(x=lid, y=mean, fill=model))
m +
  geom_bar(stat='identity', position='dodge') +
  #geom_point(stat="identity") +
  #geom_line(stat="identity") +
  geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(-100,6000), breaks=c(100,500,1000,2000, 5000)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  xlab("Dataset Size") + ylab("Recall") +
  scale_fill_manual("Model", values = c("svm" = "#505a5b", "log" = "#8f91a2", "forest" = "#343f3e"), labels = c("SVM", "LogReg", "Forest")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_line("#343f3e", size = 0.02),
        panel.grid.minor = element_line("#343f3e", size = 0.1),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position="right",
        legend.title.align=0.5)



f1 = ddply(data, c("model", "lid"), summarise,
               N    = length(f1),
               mean = mean(f1),
               sd   = sd(f1),
               se   = qt(0.975, df=N) * sd/sqrt(N)
)

m <- ggplot(f1, aes(x=lid, y=mean, fill=model))
m +
  geom_bar(stat='identity', position='dodge') +
  #geom_point(stat="identity") +
  #geom_line(stat="identity") +
  geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(-100,6000), breaks=c(100,500,1000,2000, 5000)) +
  scale_y_continuous(limits = c(0,1), breaks=seq(0,1,by=0.10)) +
  xlab("Dataset Size") + ylab("F1") +
  scale_fill_manual("Model", values = c("svm" = "#505a5b", "log" = "#8f91a2", "forest" = "#343f3e"), labels = c("SVM", "LogReg", "Forest")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_line("#343f3e", size = 0.02),
        panel.grid.minor = element_line("#343f3e", size = 0.1),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position="right",
        legend.title.align=0.5)





data <- read.csv("/home/asjacobs/workspace/webhook/res/results/conflicts_10000_forest.csv")

negation = data[data$type == 'negation',]
qos = data[data$type == 'qos',]
hierarchy = data[data$type == 'hierarchical',]
time = data[data$type == 'time',]
domain = data[data$type == 'domain',]
synonym = data[data$type == 'synonym',]
path = data[data$type == 'path',]

precision(data = factor(data$prediction), reference = factor(data$conflict))

precision(data = factor(negation$prediction), reference = factor(negation$conflict))
precision(data = factor(qos$prediction), reference = factor(qos$conflict))
precision(data = factor(hierarchy$prediction), reference = factor(hierarchy$conflict))
precision(data = factor(time$prediction), reference = factor(time$conflict))
precision(data = factor(domain$prediction), reference = factor(domain$conflict))
precision(data = factor(synonym$prediction), reference = factor(synonym$conflict))
precision(data = factor(path$prediction), reference = factor(path$conflict))

recall(data = factor(data$prediction), reference = factor(data$conflict))


recall(data = factor(negation$prediction), reference = factor(negation$conflict))
recall(data = factor(qos$prediction), reference = factor(qos$conflict))
recall(data = factor(hierarchy$prediction), reference = factor(hierarchy$conflict))
recall(data = factor(time$prediction), reference = factor(time$conflict))
recall(data = factor(domain$prediction), reference = factor(domain$conflict))
recall(data = factor(synonym$prediction), reference = factor(synonym$conflict))
recall(data = factor(path$prediction), reference = factor(path$conflict))

F_meas(data = factor(data$prediction), reference = factor(data$conflict))


F_meas(data = factor(negation$prediction), reference = factor(negation$conflict))
F_meas(data = factor(qos$prediction), reference = factor(qos$conflict))
F_meas(data = factor(hierarchy$prediction), reference = factor(hierarchy$conflict))
F_meas(data = factor(time$prediction), reference = factor(time$conflict))
F_meas(data = factor(domain$prediction), reference = factor(domain$conflict))
F_meas(data = factor(synonym$prediction), reference = factor(synonym$conflict))
F_meas(data = factor(path$prediction), reference = factor(path$conflict))



data_forest <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/learning_curve_5000_forest.csv")
data_forest$id <- as.character(data_forest$dataset)
data_forest$num_id <- as.numeric(data_forest$dataset)
data_forest[with(data_forest, order(num_id)), ]

data_forest$mean_train_mse = sapply(strsplit(as.character(data_forest$train_mse), ",", fixed=T), function(x) -1 * mean(as.numeric(x)))
data_forest$mean_test_mse = sapply(strsplit(as.character(data_forest$test_mse), ",", fixed=T), function(x) -1 *mean(as.numeric(x)))

data_svm <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/learning_curve_5000_svm.csv")
data_svm$id <- as.character(data_svm$dataset)
data_svm$num_id <- as.numeric(data_svm$dataset)
data_svm[with(data_svm, order(num_id)), ]

data_svm$mean_train_mse = sapply(strsplit(as.character(data_svm$train_mse), ",", fixed=T), function(x) -1 * mean(as.numeric(x)))
data_svm$mean_test_mse = sapply(strsplit(as.character(data_svm$test_mse), ",", fixed=T), function(x) -1 *mean(as.numeric(x)))

data_log <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/learning_curve_5000_log.csv")
data_log$id <- as.character(data_log$dataset)
data_log$num_id <- as.numeric(data_log$dataset)
data_log[with(data_log, order(num_id)), ]

data_log$mean_train_mse = sapply(strsplit(as.character(data_log$train_mse), ",", fixed=T), function(x) -1 * mean(as.numeric(x)))
data_log$mean_test_mse = sapply(strsplit(as.character(data_log$test_mse), ",", fixed=T), function(x) -1 *mean(as.numeric(x)))

data = rbind(data_forest, data_svm)
data = rbind(data, data_log)

m <- ggplot(data, aes(x=train_size))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_train_mse, color = model, shape = "Training"), size = 4) +
  geom_point(aes(y = mean_test_mse, color = model, shape = "Cross-val"), size = 4) +
  geom_line(aes(y = mean_train_mse, color = model, linetype = "Training"), size = 1  ) +
  geom_line(aes(y = mean_test_mse, color = model, linetype = "Cross-val"), size = 1 ) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  scale_x_continuous(limits = c(0, 5000)) +
  scale_y_continuous(limits = c(0.06,0.17), breaks=seq(0.06, 0.17, by=0.01)) +
  xlab("Training Samples") + ylab("MSE") +
  scale_color_manual(
    name="Model",
    values=c("#396ab1", "#da7c30", "#3e9651"),
    labels = c("Rand. Forest", "SVM", "Log. Reg."),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    )
  ) +
  scale_linetype_manual(
      name="Fit/Test",
      values=c("dashed", "solid"),
      guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    )
  ) +
  scale_shape_manual(
    name="Fit/Test",
    values=c(17, 16),
      guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    )
  )+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major.y = element_line( size=.1, color="#343f3e" ),
        panel.grid.major.x = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        #legend.justification=c(0,1),
        legend.position="top",
        legend.text=element_text(size=18),
        legend.title=element_text(size=18))

m <- ggplot(data, aes(x=train_size))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_train_mse, color = model, shape = "Training"), size = 4) +
  geom_point(aes(y = mean_test_mse, color = model, shape = "Cross-val"), size = 4) +
  geom_line(aes(y = mean_train_mse, color = model, linetype = "Training"), size = 1  ) +
  geom_line(aes(y = mean_test_mse, color = model, linetype = "Cross-val"), size = 1 ) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  scale_x_continuous(limits = c(0, 5000)) +
  scale_y_continuous(limits = c(0,0.17), breaks=seq(0, 0.17, by=0.02)) +
  xlab("Training Samples") + ylab("MSE") +
  scale_color_manual(
    name="Model",
    values=c("#396ab1", "#3e9651", "#cc2529"),
    labels = c("Rand. Forest", "SVM", "Log. Reg."),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    )
  ) +
  scale_linetype_manual(
    name="Fit/Test",
    values=c("dashed", "solid"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    )
  ) +
  scale_shape_manual(
    name="Fit/Test",
    values=c(17, 16),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    )
  )+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_line("#343f3e", size = 0.02),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position=c(0.5, 0.4),
        legend.text=element_text(size=18),
        legend.title=element_text(size=18))


data <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/learning_curve_5000_svm.csv")
data$id <- as.character(data$dataset)
data$num_id <- as.numeric(data$dataset)
data[with(data, order(num_id)), ]

data$mean_train_mse = sapply(strsplit(as.character(data$train_mse), ",", fixed=T), function(x) -1 * mean(as.numeric(x)))
data$mean_test_mse = sapply(strsplit(as.character(data$test_mse), ",", fixed=T), function(x) -1 *mean(as.numeric(x)))

#data <- rbind(c('forest','5000',0, '', '',5000,5000, 0.0, 0.15, 5000), data)




m <- ggplot(data, aes(x=train_size))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_train_mse, color = "Training", shape = "Training"), size = 4) +
  geom_point(aes(y = mean_test_mse, color = "Cross-validation", shape = "Cross-validation"), size = 4) +
  geom_line(aes(y = mean_train_mse, color = "Training", linetype = "Training"), size = 2  ) +
  geom_line(aes(y = mean_test_mse, color = "Cross-validation", linetype = "Cross-validation"), size = 2 ) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0.10,0.18), breaks=seq(0,0.18, by=0.02)) +
  xlab("Training Samples") + ylab("MSE") +
  scale_linetype_manual(name="Guide1", values=c("dashed","solid"))+
  scale_color_manual(name="Guide1", values=c('#505a5b','#94b0da'))+
  scale_shape_manual(name="Guide1", values=c(15,16))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_line("#343f3e", size = 0.02),
        panel.grid.minor = element_line("#343f3e", size = 0.1),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position=c(0.65, 0.95),
        legend.text=element_text(size=26),
        legend.title=element_blank())





data <- read.csv("/home/asjacobs/workspace/lumi-webhook/res/results/learning_curve_5000_log.csv")
data$id <- as.character(data$dataset)
data$num_id <- as.numeric(data$dataset)
data[with(data, order(num_id)), ]

data$mean_train_mse = sapply(strsplit(as.character(data$train_mse), ",", fixed=T), function(x) -1 * mean(as.numeric(x)))
data$mean_test_mse = sapply(strsplit(as.character(data$test_mse), ",", fixed=T), function(x) -1 *mean(as.numeric(x)))

#data <- rbind(c('forest','5000',0, '', '',5000,5000, 0.0, 0.15, 5000), data)

m <- ggplot(data, aes(x=train_size))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_train_mse, color = "Training", shape = "Training"), size = 4) +
  geom_point(aes(y = mean_test_mse, color = "Cross-validation", shape = "Cross-validation"), size = 4) +
  geom_line(aes(y = mean_train_mse, color = "Training", linetype = "Training"), size = 2  ) +
  geom_line(aes(y = mean_test_mse, color = "Cross-validation", linetype = "Cross-validation"), size = 2 ) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0.1,0.18), breaks=seq(0,0.18, by=0.02)) +
  xlab("Training Samples") + ylab("MSE") +
  scale_linetype_manual(name="Guide1", values=c("dashed","solid"))+
  scale_color_manual(name="Guide1", values=c('#505a5b','#94b0da'))+
  scale_shape_manual(name="Guide1", values=c(15,16))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_line("#343f3e", size = 0.02),
        panel.grid.minor = element_line("#343f3e", size = 0.1),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.justification=c(0,1),
        legend.position=c(0.65, 0.95),
        legend.text=element_text(size=26),
        legend.title=element_blank())




data <- read.csv("/Users/asjacobs/workspace/lumi/webhook/res/results/extraction/extraction_feedback_mean.csv")


m <- ggplot(data, aes(x=idx))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_recall, color = "Recall"), size = 3) +
  geom_line(aes(y = mean_recall, color = "Recall"), size = 1) +
  geom_errorbar(aes(ymin=rec_ci_start, ymax=rec_ci_end), colour="#343f3e", width=0.8, size=0.8, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0, 1), breaks=seq(0,1, by=0.2)) +
  xlab("# of the Test Sample") + ylab("Metric") +
  scale_linetype_manual(
    name="Guide1",
    values=c("dashed","solid"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    ))+
  scale_color_manual(
    name="Guide1",
    values=c("#da7c30"),
    guide = guide_legend(
     direction = "horizontal",
     title.position = "top",
     title.hjust = 0.5
    ))+
  scale_shape_manual(
    name="Guide1",
    values=c(15,16),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.position="top",
        legend.text=element_text(size=28),
        legend.title=element_blank())



m <- ggplot(data, aes(x=idx))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = mean_precision, color = "Precision"), size = 3) +
  geom_line(aes(y = mean_precision, color = "Precision"), size = 1  ) +
  geom_errorbar(aes(ymin=prec_ci_start, ymax=prec_ci_end), colour="#343f3e", width=0.8, size=0.8, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0, 1), breaks=seq(0,1, by=0.2)) +
  xlab("# of the Test Sample") + ylab("Metric") +
  scale_linetype_manual(
    name="Guide1",
    values=c("dashed","solid"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    ))+
  scale_color_manual(
    name="Guide1",
    values=c("#396ab1", "#da7c30"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  scale_shape_manual(
    name="Guide1",
    values=c(15,16),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.position="top",
        legend.text=element_text(size=28),
        legend.title=element_blank())


data <- read.csv("/Users/asjacobs/workspace/lumi/webhook/res/results/extraction/extraction_feedback_single.csv")

m <- ggplot(data, aes(x=feedback_round))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = precision, color = "Precision", shape = "Precision"), size = 3) +
  geom_point(aes(y = recall, color = "Recall", shape = "Recall"), size = 3) +
  geom_line(aes(y = precision, color = "Precision", linetype = "Precision"), size = 1) +
  geom_line(aes(y = recall, color = "Recall", linetype = "Recall"), size =  1) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0, 1), breaks=seq(0,1, by=0.2)) +
  xlab("# of the Test Sample") + ylab("Metric") +
  scale_linetype_manual(
    name="Guide1",
    values=c("dashed","solid"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    ))+
  scale_color_manual(
    name="Guide1",
    values=c("#396ab1", "#da7c30"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  scale_shape_manual(
    name="Guide1",
    values=c(15,16),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.position="top",
        legend.text=element_text(size=28),
        legend.title=element_blank())


m <- ggplot(data, aes(x=feedback_round))
m +
  #geom_bar(stat='identity', position='dodge') +
  geom_point(aes(y = f1_score, color = "F1 Score", shape = "F1 Score"), size = 3) +
  geom_line(aes(y = f1_score, color = "F1 Score", linetype = "F1 Score"), size = 1) +
  #geom_errorbar(aes(ymin=mean - se, ymax=mean + se), colour="black", width=0.1, position=position_dodge(0.8)) +
  #scale_x_continuous(limits = c(100,5000)) +
  scale_y_continuous(limits = c(0, 1), breaks=seq(0,1, by=0.2)) +
  xlab("# of the Test Sample") + ylab("Metric") +
  scale_linetype_manual(
    name="Guide1",
    values=c("dashed","solid"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top"
    ))+
  scale_color_manual(
    name="Guide1",
    values=c("#da9e94", "#da7c30"),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  scale_shape_manual(
    name="Guide1",
    values=c(15,16),
    guide = guide_legend(
      direction = "horizontal",
      title.position = "top",
      title.hjust = 0.5
    ))+
  #scale_fill_manual("Colour", values = c("mean_test_mse" = , "mean_train_mse" = ), labels = c("SVM", "LogReg")) +
  theme(text = element_text(colour="#343f3e", size=28, family="Roboto Light"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_blank(),
        panel.border = element_blank(),
        axis.line.x = element_line(color = '#343f3e'),
        axis.line.y = element_line(color = '#343f3e'),
        axis.line = element_line(colour = "#343f3e"),
        legend.position="top",
        legend.text=element_text(size=28),
        legend.title=element_blank())

