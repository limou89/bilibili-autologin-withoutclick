##api处理

# Chaojiying_Client类  用于提交要识别的图片  返回json结果
class Chaojiying_Client(object):
    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf-8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        logging.info(r.json())
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        logging.info(r.json())
        print(r.json)
        return r.json()


##模拟点击

from selenium import webdriver
from time import sleep
from PIL import Image
from selenium.webdriver import ActionChains
import random
import requests
from hashlib import md5
import logging

##日志输出和 webdriver.Chrome() 配置
# 日志输出配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
chrome_driver = r'[chromedriver.exe所在绝对路径]'
options = webdriver.ChromeOptions()
# 关闭左上方 Chrome 正受到自动测试软件的控制的提示
#options.add_experimental_option('useAutomationExtension', False)
#options.add_experimental_option("excludeSwitches", ['enable-automation'])
# 使用Service对象
service = Service(chrome_driver)
browser = webdriver.Chrome(service=service, options=options)

# 登录函数   访问页面->输出账号、密码->点击登录
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
def login():
    browser.get('https://passport.bilibili.com/login')
    browser.maximize_window()
    
    try:
        # 等待并定位用户名输入框
        username = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="请输入账号"]'))
        )
        
        # 定位密码输入框
        password = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
        )
        
        # 输入账号密码
        username.send_keys('b站账号')
        
        password.send_keys('b站密码')
        
        # 找到登录按钮并点击
        login_btn = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_primary'))  # 根据实际情况调整
        )
        login_btn.click()
        
        time.sleep(random.random()*3)
        
    except Exception as e:
        print(f"登录过程中出现错误: {e}")

        
import time
import random
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw
from time import sleep

class CaptchaCoordinateHandler:
    def __init__(self, browser):
        self.browser = browser
        self.page_size = None           # page.png的尺寸
        self.code_position = None       # code.png在page.png中的绝对位置 [left, top, width, height]
        self.code_size = None          # code.png的尺寸
        self.small_size = None         # small_img.png的尺寸
        self.scale_ratio = None        # 缩放比例
        self.code_img_element = None   # 验证码元素
        
    def save_img(self):
        """保存验证码图片并记录位置信息"""
        try:
            # 找到验证码容器
            code_img_ele = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_wrap'))
            )
            self.code_img_element = code_img_ele
            
            # 等待加载完成
            try:
                WebDriverWait(self.browser, 5).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_loading'))
                )
            except:
                pass
            
            time.sleep(2)
            
            # 获取设备像素比率
            device_pixel_ratio = self.browser.execute_script("return window.devicePixelRatio;")
            
            # 获取页面滚动位置
            scroll_x = self.browser.execute_script("return window.pageXOffset;")
            scroll_y = self.browser.execute_script("return window.pageYOffset;")
            
            # 获取元素位置和大小（视口坐标）
            location = code_img_ele.location
            size = code_img_ele.size
            
            print(f"元素位置(视口): {location}")
            print(f"元素大小: {size}")
            print(f"页面滚动: scroll_x={scroll_x}, scroll_y={scroll_y}")
            print(f"设备像素比: {device_pixel_ratio}")
            
            # 计算在page.png中的绝对位置（物理像素）
            abs_x = location['x'] + scroll_x
            abs_y = location['y'] + scroll_y
            
            left = int(abs_x * device_pixel_ratio)
            top = int(abs_y * device_pixel_ratio)
            width = int(size['width'] * device_pixel_ratio)
            height = int(size['height'] * device_pixel_ratio)
            
            # 截取整个页面
            self.browser.save_screenshot('page.png')
            
            # 记录page.png尺寸
            page_img = Image.open('page.png')
            self.page_size = page_img.size
            print(f"page.png尺寸: {self.page_size}")
            
            # 记录code.png在page.png中的位置
            self.code_position = [left, top, width, height]
            print(f"code.png在page.png中的位置: left={left}, top={top}, width={width}, height={height}")
            
            # 裁剪验证码图片
            right = left + width
            bottom = top + height
            captcha_img = page_img.crop((left, top, right, bottom))
            captcha_img.save('code.png')
            self.code_size = captcha_img.size
            
            print(f"code.png尺寸: {self.code_size}")
            print(f"验证码图片保存成功！")
            
            return True
            
        except Exception as e:
            print(f"保存验证码图片失败: {e}")
            return False

    def narrow_img(self):
        """缩小图片并记录缩放比例"""
        try:
            code = Image.open('./code.png')
            original_size = code.size
            print(f"原始code.png尺寸: {original_size}")
            
            # 计算缩放比例，确保不超过460x310
            max_width, max_height = 460, 310
            width_ratio = max_width / original_size[0]
            height_ratio = max_height / original_size[1]
            scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大
            
            new_width = int(original_size[0] * scale_ratio)
            new_height = int(original_size[1] * scale_ratio)
            
            small_img = code.resize((new_width, new_height), Image.Resampling.LANCZOS)
            small_img.save('./small_img.png')
            
            self.small_size = small_img.size
            self.scale_ratio = scale_ratio
            
            print(f"small_img.png尺寸: {self.small_size}")
            print(f"缩放比例: {scale_ratio}")
            
            return scale_ratio
            
        except Exception as e:
            print(f"缩放图片失败: {e}")
            return 1.0

    def submit_img(self):
        """提交图片给超级鹰识别"""
        try:
            chaojiying = Chaojiying_Client('超级鹰账号', '超级鹰密码', '申请软件ID')
            with open('./small_img.png', 'rb') as f:
                im = f.read()
            result = chaojiying.PostPic(im, 9004)['pic_str']
            logging.info(f"超级鹰识别结果: {result}")
            return result
        except Exception as e:
            print(f"提交识别失败: {e}")
            return ""

    def parse_data(self, result):
        """解析超级鹰返回的坐标"""
        node_list = []
        print(f"原始识别结果: {result}")
        
        if not result:
            return node_list
            
        try:
            if '|' in result:
                nums = result.split('|')
                for num in nums:
                    if ',' in num:
                        x, y = map(int, num.split(','))
                        node_list.append([x, y])
            else:
                if ',' in result:
                    x, y = map(int, result.split(','))
                    node_list.append([x, y])
            
            print(f"解析后坐标(small_img.png中): {node_list}")
            return node_list
            
        except Exception as e:
            print(f"解析坐标失败: {e}")
            return []

    def convert_to_page_coordinates(self, small_img_coords):
        """
        转换坐标：
        small_img坐标 → code.png坐标 → page.png绝对坐标
        转换逻辑
        将缩小图中的坐标还原为原始验证码图中的坐标
        将验证码图中的坐标转换为整个页面截图中的绝对坐标
        """
        if not all([self.scale_ratio, self.code_position]):
            print("缺少必要的位置信息")
            return []
        
        page_coords = []
        
        print("=== 坐标转换过程 ===")
        print(f"small_img.png尺寸: {self.small_size}")
        print(f"code.png尺寸: {self.code_size}")
        print(f"page.png尺寸: {self.page_size}")
        print(f"code.png在page.png中的位置: {self.code_position}")
        print(f"缩放比例: {self.scale_ratio}")
        
        for i, coord in enumerate(small_img_coords):
            small_x, small_y = coord[0], coord[1]
            
            # 步骤1: small_img坐标 → code.png坐标（放缩）
            code_x = small_x / self.scale_ratio
            code_y = small_y / self.scale_ratio
            
            # 步骤2: code.png坐标 → page.png绝对坐标（加上偏移）
            page_x = code_x + self.code_position[0]  # 加上left偏移
            page_y = code_y + self.code_position[1]  # 加上top偏移
            
            page_coords.append([page_x, page_y])
            
            print(f"点{i+1}: small_img({small_x},{small_y}) → code.png({code_x:.1f},{code_y:.1f}) → page.png({page_x:.1f},{page_y:.1f})")
        
        return page_coords

    def click_page_coordinates(self, page_coords):
        """
        使用page.png中的绝对坐标进行点击
        """
        if not page_coords:
            print("坐标列表为空")
            return False
        
        try:
            print("=== 开始点击坐标 ===")
            
            for i, coord in enumerate(page_coords):
                page_x, page_y = coord[0], coord[1]
                
                print(f"准备点击第{i+1}个点: page.png中的绝对坐标({page_x:.1f}, {page_y:.1f})")
                # 方法1: 直接移动到页面绝对坐标点击
                try:
                    
                    # 注意：这里需要考虑设备像素比的逆转换
                    device_pixel_ratio = self.browser.execute_script("return window.devicePixelRatio;")
                    
                    # 转换回逻辑像素坐标
                    logical_x = page_x / device_pixel_ratio
                    logical_y = page_y / device_pixel_ratio
                    
                    # 获取当前页面滚动位置
                    scroll_x = self.browser.execute_script("return window.pageXOffset;")
                    scroll_y = self.browser.execute_script("return window.pageYOffset;")
                    
                    # 转换为视口坐标
                    viewport_x = logical_x - scroll_x
                    viewport_y = logical_y - scroll_y
                    
                    print(f"逻辑坐标: ({logical_x:.1f}, {logical_y:.1f})")
                    print(f"视口坐标: ({viewport_x:.1f}, {viewport_y:.1f})")
                    
                    # 使用JavaScript直接点击
                    click_script = f"""
                    var event = new MouseEvent('click', {{
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': {viewport_x},
                        'clientY': {viewport_y}
                    }});
                    document.elementFromPoint({viewport_x}, {viewport_y}).dispatchEvent(event);
                    """
                    
                    self.browser.execute_script(click_script)
                    print(f"第{i+1}个点击成功")
                    
                    sleep(random.uniform(0.5, 1.0))

                # 方法2:使用元素相对坐标
                except Exception as e:
                    print(f"第{i+1}个点击失败: {e}")
                    
                    try:
                        if self.code_img_element:
                            element_location = self.code_img_element.location
                            relative_x = logical_x - element_location['x']
                            relative_y = logical_y - element_location['y']
                            
                            ActionChains(self.browser).move_to_element_with_offset(
                                self.code_img_element, relative_x, relative_y
                            ).click().perform()
                            
                            print(f"第{i+1}个点击成功(备用方法)")
                    except:
                        print(f"第{i+1}个点击完全失败")
                        continue
            
            # 等待后点击确认
            sleep(random.uniform(1, 2))
            return self.click_confirm_button()
            
        except Exception as e:
            print(f"点击过程失败: {e}")
            return False

    def click_confirm_button(self):
        """点击确认按钮"""
        selectors = [
            (By.CLASS_NAME, 'geetest_commit_tip')
        ]
        ##存储可能的确认按钮
        for selector_type, selector_value in selectors:
            try:
                commit_btn = WebDriverWait(self.browser, 3).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                commit_btn.click()
                print('确认按钮点击成功！')
                return True
            except:
                continue
        
        print("未找到可点击的确认按钮")
        return False

    def debug_save_all_marked_images(self, small_coords, page_coords):
        """调试：在所有图片上标记坐标点"""
        try:
            # 1. 在small_img.png上标记
            small_img = Image.open('./small_img.png')
            draw = ImageDraw.Draw(small_img)
            for i, coord in enumerate(small_coords):
                x, y = coord[0], coord[1]
                radius = 3
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='red', width=2)
                draw.text((x+5, y-5), str(i+1), fill='red')
            small_img.save('./debug_small_marked.png')
            
            # 2. 在code.png上标记（转换后的坐标）
            code_img = Image.open('./code.png')
            draw = ImageDraw.Draw(code_img)
            for i, small_coord in enumerate(small_coords):
                code_x = small_coord[0] / self.scale_ratio
                code_y = small_coord[1] / self.scale_ratio
                radius = 5
                draw.ellipse([code_x-radius, code_y-radius, code_x+radius, code_y+radius], 
                           outline='blue', width=2)
                draw.text((code_x+8, code_y-8), str(i+1), fill='blue')
            code_img.save('./debug_code_marked.png')
            
            # 3. 在page.png上标记（最终坐标）
            page_img = Image.open('./page.png')
            draw = ImageDraw.Draw(page_img)
            for i, coord in enumerate(page_coords):
                x, y = coord[0], coord[1]
                radius = 8
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='green', width=3)
                draw.text((x+10, y-10), str(i+1), fill='green')
            page_img.save('./debug_page_marked.png')
            
            print("调试图片已保存:")
            print("- debug_small_marked.png (small_img上的识别点)")
            print("- debug_code_marked.png (code.png上的转换点)")
            print("- debug_page_marked.png (page.png上的最终点击点)")
            
        except Exception as e:
            print(f"保存调试图片失败: {e}")

def process_captcha_with_absolute_coords(browser):
    """处理验证码"""
    handler = CaptchaCoordinateHandler(browser)
    
    try:
        print("=== 开始处理验证码 ===")
        
        # 1. 保存验证码图片并记录位置
        if not handler.save_img():
            return False
        
        # 2. 缩放图片
        scale_ratio = handler.narrow_img()
        
        # 3. 提交识别
        result = handler.submit_img()
        if not result:
            print("识别失败")
            return False
        
        # 4. 解析small_img中的坐标
        small_coords = handler.parse_data(result)
        if not small_coords:
            print("坐标解析失败")
            return False
        
        # 5. 转换为page.png中的绝对坐标
        page_coords = handler.convert_to_page_coordinates(small_coords)
        if not page_coords:
            print("坐标转换失败")
            return False
        
        # 6. 调试：保存标记图片
        handler.debug_save_all_marked_images(small_coords, page_coords)
        
        # 7. 使用绝对坐标点击
        success = handler.click_page_coordinates(page_coords)
        return success
        
    except Exception as e:
        print(f"验证码处理失败: {e}")
        return False



def main():
    # 进入登录界面，输入账号密码
    login()
    # 使用示例：
# 使用方法：
    success = process_captcha_with_absolute_coords(browser)
    print("登录完成，按Enter键关闭浏览器...")
    input()
main()