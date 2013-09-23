
def RamActivityVirtualColumn(dbrow):
# this does not work because the dbrow does not have a cfg attrib and we don't have a global one.
# the RamDetail class will handle it.
#   return cfg.ramaltypes.Get(dbrow.assemblyLineTypeID).activityID
	return None

