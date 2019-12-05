# Mini Stadia

* Google Stadia에서 아이디어를 얻어 한 번 만들어본 프로젝트입니다.
  * <https://namu.wiki/w/Stadia>
<br></br>
* 성능
  * 화면 전송과 조작 신호 전송은 잘 작동합니다.
  * 하지만 플레이가 거의 불가능할 정도로 화면이 끊깁니다.
  * 구현했다는 것에 의의를 두었습니다...
<br></br>
* 실행 방법 (컴퓨터에 Python이 깔려있어야 합니다)

  1. repository를 클론합니다.
  ```
  git clone https://github.com/tunde02/networkprogramming_termproject.git
  ```
  
  2. 가상환경을 생성하고 실행합니다.
  ```
  python -m venv your_virtual_environment_name
  
  your_virtual_environment_name\Script\activate
  ```
  3. 가상환경에 패키지들을 다운로드합니다.
  ```
  pip install -r requirements.txt
  ```
  
  4. source폴더로 들어가 Python 파일을 실행합니다.
  ```
  cd source
  
  python client.py
  ```
