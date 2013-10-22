def Singleton(dbrow):
	# used as property getter by certain cache objects
	if dbrow.quantity < 0:
		return 1
	else:
		if 30000000 <= dbrow.locationID < 40000000:
			return 1
	return 0


def StackSize(dbrow):
	# used as property getter by certain cache objects
	qty = dbrow.quantity
	if qty < 0:
		return 1
	return qty


def RamActivityVirtualColumn(dbrow):
# this does not work because the dbrow does not have a cfg attrib and we don't have a global one.
# the RamDetail class will handle it.
#   return cfg.ramaltypes.Get(dbrow.assemblyLineTypeID).activityID
	return None

