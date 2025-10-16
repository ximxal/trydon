import novapi
import time
import math
from mbuild.encoder_motor import encoder_motor_class
from mbuild import power_expand_board
from mbuild import gamepad
from mbuild.led_matrix import led_matrix_class
from mbuild.smart_camera import smart_camera_class
from mbuild.ranging_sensor import ranging_sensor_class
from mbuild.smartservo import smartservo_class
from mbuild import power_manage_module


class donttrythisathome:
    def __init__(self):
        self.encoder_motor_M1 = encoder_motor_class("M1", "INDEX1")
        self.encoder_motor_M2 = encoder_motor_class("M2", "INDEX1")
        self.encoder_motor_M3 = encoder_motor_class("M3", "INDEX1")
        self.encoder_motor_M4 = encoder_motor_class("M4", "INDEX1")
        self.encoder_motor_M6 = encoder_motor_class("M6", "INDEX1")

        self.blushless_motor = "BL1"
        self.feed_lower = "DC4"
        self.feed_mid = "DC3"
        self.feed_upper = "DC6"
        self.tong = "DC1"
        self.flick_block = "DC5"
        self.lift_dc = "DC2"

        self.servo_level = smartservo_class("M5", "INDEX1")
        self.CTRL_MODE = 0

        # State variables
        self.set_Bl = 0
        self.auto_set = 0
        self.tong_set = 0
        self.L2_toggle_step = 0
        self.L2_last_state = False
        self.feed_middle_toggle = False
        self.l1_last_state = False
        self.r1_active = False
        self.bl_hard_active = False
        self.bl_smooth_active = False
        self.auto_key_last = False
        self.arm_on_state = False
        self.n1_last_state = False
        self.n4_last_state = False
        self.bl_key_last = False

        # Block Expro
        self.block_expro_active = False
        self.r_thumb_last_state = False
        self.block_expro_start_time = 0.0
        self.block_expro_last_toggle_time = 0.0
        self.block_expro_power_on = False
        self.block_expro_toggle_interval = 0.2
        self.block_expro_duration = 5.0
        self.block_expro_power_value = -10

        self.servo_control_zero()

    def change_mode(self):
        if novapi.timer() > 0.9:
            if self.CTRL_MODE == 0:
                self.CTRL_MODE = 1
            else:
                self.CTRL_MODE = 0
            novapi.reset_timer()
            
    # -------------------- Movement Functions --------------------
    def set_motor_speed(self, ul, ur, ll, lr):
        self.encoder_motor_M1.set_speed(ul)
        self.encoder_motor_M2.set_speed(ur)
        self.encoder_motor_M3.set_speed(ll)
        self.encoder_motor_M4.set_speed(lr)
    
    def set_motor_degree(self, ul, ur, ll, lr, r):
        self.encoder_motor_M1.move(ul, r)
        self.encoder_motor_M2.move(ur, r)
        self.encoder_motor_M3.move(ll, r)
        self.encoder_motor_M4.move(lr, r)
    
    def spin_right(self):
        self.set_motor_speed(-30, -30, -30, -30)

    def spin_left(self):
        self.set_motor_speed(30, 30, 30, 30)

    def move_forward(self):
        self.set_motor_speed(60, -85, 85, -90)
        
    def auto_forward(self):
        self.set_motor_speed(100, -100, 100, -100)
        
    def move_forward_slow(self):
        self.set_motor_speed(40, -55, 60, -40)

    def move_backward(self):
        self.set_motor_speed(-65, 70, -70, 75)

    def move_backward_slow(self):
        self.set_motor_speed(-45, 50, -50, 55)

    def move_right_sideway(self):
        self.set_motor_speed(75, 75, -90, -70)

    def move_left_sideway(self):
        self.set_motor_speed(-75, -100, 75, 100)

    def stop_motor(self):
        self.set_motor_speed(0, 0, 0, 0)

    def move_suddenly(self):
        for _ in range(2):
            self.set_motor_speed(40, -40, 40, -40, 10)
            time.sleep(0.4)
            self.set_motor_speed(0, 0, 0, 0, 0)
            time.sleep(0.4)

    # -------------------- Brushless Motor --------------------
    def Bl_hard(self):
        if not self.bl_smooth_active:
            power_expand_board.set_power(self.blushless_motor, 90 if not self.bl_hard_active else 0)
            self.bl_hard_active = not self.bl_hard_active
            time.sleep(0.1)

    def BL_smooth(self):
        if not self.bl_hard_active:
            power_expand_board.set_power(self.blushless_motor, 60 if not self.bl_smooth_active else 0)
            self.bl_smooth_active = not self.bl_smooth_active
            time.sleep(0.1)

    # -------------------- Servo --------------------
    def servo_control_down(self):
        self.servo_level.move_to(10, 25)

    def servo_control_zero(self):
        self.servo_level.move_to(0, 20)

    def servo_control_up(self):
        self.servo_level.move_to(-35, 25)

    def servo_control_block(self):
        self.servo_level.move_to(30, 20)

    def servo_control_up_2(self):
        self.servo_level.move_to(-26, 20)
        
    #L2 servo
    def servo_control_up_L2_1(self):
        self.servo_level.move_to(-10, 20)
        
    def servo_control_up_L2_2(self):
        self.servo_level.move_to(0, 20)
        
    def servo_control_up_L2_3(self):
        self.servo_level.move_to(10, 20) 

    # -------------------- Feeder --------------------
    def feed_middle_down(self):
        self.encoder_motor_M6.set_power(80)
        power_expand_board.set_power(self.feed_lower, 100)
        power_expand_board.set_power(self.feed_mid, -80)

    def feed_middle_down_slow_with_upper(self):
        self.encoder_motor_M6.set_power(80)
        power_expand_board.set_power(self.feed_lower, 100)
        power_expand_board.set_power(self.feed_mid, -70)
        power_expand_board.set_power(self.feed_upper, -100)

    def feed_middle_down_slow_with_upper_2(self):
        self.encoder_motor_M6.set_power(50)
        power_expand_board.set_power(self.feed_lower, 100)
        power_expand_board.set_power(self.feed_mid, -25)
        power_expand_board.set_power(self.feed_upper, -60)

    def feed_set_zero(self):
        self.encoder_motor_M6.set_power(0)
        power_expand_board.set_power(self.feed_lower, 0)
        power_expand_board.set_power(self.feed_mid, 0)
        power_expand_board.set_power(self.feed_upper, 0)

    def feed_reverse(self):
        self.encoder_motor_M6.set_power(-70)
        power_expand_board.set_power(self.feed_lower, -55)
        power_expand_board.set_power(self.feed_mid, 80)
        power_expand_board.set_power(self.feed_upper, 100)

    # -------------------- Arm / Tong --------------------
    def arm_on(self):
        power_expand_board.set_power(self.tong, 35)

    def arm_off(self):
        power_expand_board.set_power(self.tong, -15)

    def arm_set_zero(self):
        power_expand_board.set_power(self.tong, 0)

    # -------------------- Lifter --------------------
    def lift_up(self):
        power_expand_board.set_power(self.lift_dc, 100)

    def lift_down(self):
        power_expand_board.set_power(self.lift_dc, -100)

    def lift_frozen(self):
        power_expand_board.set_power(self.lift_dc, 8)

    # -------------------- Block Flick --------------------
    def block_up(self):
        power_expand_board.set_power(self.flick_block, 80)

    def block_back_to_zero(self):
        power_expand_board.set_power(self.flick_block, 0)

    def block_expro(self):
        power_expand_board.set_power(self.flick_block, self.block_expro_power_value)
        
    # -------------------- Control System --------------------
    def control_system(self):
        ly = gamepad.get_joystick("Ly")
        rx = gamepad.get_joystick("Rx")
        lx = gamepad.get_joystick("Lx")

        move_handled = False

        if rx >= 90:
            self.set_motor_speed(-90, -90, -90, -90)
            move_handled = True
        elif rx >= 50:
            self.set_motor_speed(-70, -70, -70, -70)
            move_handled = True
        elif rx <= -90:
            self.set_motor_speed(90, 90, 90, 90)
            move_handled = True
        elif rx <= -50:
            self.set_motor_speed(70, 70, 70, 70)
            move_handled = True
        elif ly >= 40:
            self.move_forward()
            move_handled = True
        elif ly <= -40:
            self.move_backward()
            move_handled = True
        elif lx >= 40:
            self.move_left_sideway()
            move_handled = True
        elif lx <= -40:
            self.move_right_sideway()
            move_handled = True

        if not move_handled:
            self.stop_motor()

        # FEED CONTROLS
        l1 = gamepad.is_key_pressed("L1")
        r1 = gamepad.is_key_pressed("R1")

        if l1 and not self.l1_last_state:
            if self.r1_active:
                self.r1_active = False
            self.feed_middle_toggle = not self.feed_middle_toggle
        self.l1_last_state = l1

        if r1 and not self.r1_active:
            self.feed_middle_toggle = False
            self.r1_active = True
        if not r1 and self.r1_active:
            self.r1_active = False

        if self.r1_active:
            self.feed_middle_down_slow_with_upper()
        elif self.feed_middle_toggle:
            self.feed_middle_down()
        else:
            self.feed_set_zero()

        if gamepad.is_key_pressed("R2"):
            self.feed_reverse()
            time.sleep(0.01)

        # BRUSHLESS MOTOR
        if gamepad.is_key_pressed("Left"):
            self.BL_smooth()

        if gamepad.is_key_pressed("+") and not self.bl_key_last:
            self.Bl_hard()
        self.bl_key_last = gamepad.is_key_pressed("+")

        # SERVO CONTROL
        if gamepad.is_key_pressed("N2"):
            self.servo_control_up()
            time.sleep(0.02)
        elif gamepad.is_key_pressed("N3"):
            self.servo_control_down()
            time.sleep(0.02)
        elif gamepad.is_key_pressed("≡"):
            self.servo_control_zero()
            time.sleep(0.02)
        elif gamepad.is_key_pressed("Right"):
            self.servo_control_up_2()
            time.sleep(0.02)

        # BLOCK CONTROL
        l_thumb_current = gamepad.is_key_pressed("L_Thumb")
        r_thumb_current = gamepad.is_key_pressed("R_Thumb")

        if not hasattr(self, 'block_flick_mode'):
            self.block_flick_mode = 0
            self.l_thumb_last_state = False
            self.r_thumb_last_state = False

        if r_thumb_current and not self.r_thumb_last_state:
            if self.block_flick_mode == 2:
                self.block_flick_mode = 0
                power_expand_board.set_power(self.flick_block, 0)
            else:
                self.block_flick_mode = 2
                power_expand_board.set_power(self.flick_block, -20)
        self.r_thumb_last_state = r_thumb_current

        if l_thumb_current and not self.l_thumb_last_state:
            if self.block_flick_mode == 1:
                self.block_flick_mode = 0
                power_expand_board.set_power(self.flick_block, 0)
            elif self.block_flick_mode == 0:
                self.block_flick_mode = 1
                power_expand_board.set_power(self.flick_block, 80)
        self.l_thumb_last_state = l_thumb_current

        # ARM CONTROL
        n1_pressed = gamepad.is_key_pressed("N1")
        n4_pressed = gamepad.is_key_pressed("N4")
        lifting = gamepad.is_key_pressed("Up") or gamepad.is_key_pressed("Down")

        if n4_pressed and not lifting:
            self.arm_on_state = False
            self.arm_off()
        else:
            if n1_pressed and not self.n1_last_state:
                self.arm_on_state = True

            if self.arm_on_state:
                self.arm_on()
            else:
                self.arm_set_zero()

        self.n1_last_state = n1_pressed
        self.n4_last_state = n4_pressed

        # LIFT CONTROL
        if gamepad.is_key_pressed("Up"):
            self.lift_up()
        elif gamepad.is_key_pressed("Down"):
            self.lift_down()
        else:
            self.lift_frozen()


class automatic(donttrythisathome):
    def auto_left(self):
        self.block_up()
        time.sleep(0.1)
        self.auto_forward()
        time.sleep(0.8)
        self.move_suddenly()
        time.sleep(0.1)
        self.block_expro()
        time.sleep(0.4)
        self.move_backward_slow()
        time.sleep(0.5)
        self.servo_control_down()
        time.sleep(1)
        self.stop_motor()
        time.sleep(0.2)

    def auto_right(self):
        self.block_up()
        time.sleep(0.1)
        self.move_forward()
        time.sleep(0.8)
        self.move_suddenly()
        time.sleep(0.1)
        self.block_expro()
        time.sleep(0.4)
        self.move_backward_slow()
        time.sleep(0.5)
        self.servo_control_down()
        time.sleep(1)
        self.stop_motor()
        time.sleep(0.2)

    def Auto_Mode(self):
        if gamepad.is_key_pressed("N1"):
            self.auto_left()
            time.sleep(0.2)
        elif gamepad.is_key_pressed("N4"):
            self.auto_right()
            time.sleep(0.2)
        elif gamepad.is_key_pressed("N3"):
            self.encoder_motor_M1.set_power(0)
            self.encoder_motor_M2.set_power(0)
            self.encoder_motor_M3.set_power(0)
            self.encoder_motor_M4.set_power(0)
            time.sleep(0.2)
        else:
            pass
            

# -------------------- MAIN LOOP --------------------
robot = donttrythisathome()
robot2 = automatic()

while True:
    if power_manage_module.is_auto_mode():
        automatic.auto_left #แก้ auto ซ้าย, ขวา ตรงนี้
        while power_manage_module.is_auto_mode():
            pass
    else:
        if gamepad.is_key_pressed("L2"):
            robot.change_mode()
            time.sleep(0.3)
        else:
            if robot.CTRL_MODE == 0:
                robot.control_system()
            else:
                robot2.Auto_Mode()
