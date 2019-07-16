library(rpart)
dosya<- read.csv("dosya_object.csv")
model = rpart(Object ~ ., data = dosya)
model
summary(model)
install.packages("rpart.plot")
library(rpart.plot)
rpart.plot(model, extra =4)
