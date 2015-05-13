#import module1
import logger
with open('session.txt', 'r') as f:
  sessionID = int(f.readline())

#logger = module1.logger()
logger = logger.logger(sessionID, "JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj") #JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj