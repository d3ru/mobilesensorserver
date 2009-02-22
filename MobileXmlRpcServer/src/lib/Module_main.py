# Main class for testing Modules for features on N95
#
# imports for functions
import sms, rot, gps, gsm
import e32, appuifw, thread
lock=e32.Ao_lock()
#################################################
#################      Demo's      ##############
#################################################

def demo_sms():
	sms_module=sms.sms()
	msgs = sms_module.get_msg_ids()
	print 'ids in box:'
	for box in msgs:
		print box
		for id in msgs[box]:
			print id
		print '___'
	msg_id=msgs['draft']
	print 'content of first draft msg:'
	print sms_module.get_msg_content('draft', msg_id[0])
	print 'time of first draft msg:'
	print sms_module.get_msg_time('draft', msg_id[0])
	print 'address of first draft msg:'
	print sms_module.get_msg_address('draft', msg_id[0])

def demo_rot():
	sensor_data=''
	def callback(status):
		sensor_data=status
	rot_module=rot
	rot_module.connect(callback)
	x=0;
	while x<100:
		print sensor_data
		e32.ao_sleep(0.5)
		x=x+1

def demo_gps():
	print 'testing gps'
	print gps.get_last_position()
	#print gps.get_current_position()
	print 'done'
	
def demo_gsm():
	print 'testing gsm'
	print gsm.get_gsm_location()
	print 'done'

#################################################
#################################################
appuifw.app.title=u'Module Tester'
appuifw.app.exit_key_handler=lock.signal
demo_gps()
demo_gsm()
# demo_rot()
lock.wait()