사용 방법은 상단의 Wiki 탭을 확인해주세요!

# 전역
1. 플레이어 목록: 게임에 참여한 플레이어들의 DM 채널 모음 // List<플레이어 DM 채널>
2. 이모티콘: 각각의 이모티콘이 의미하는 플레이어 목록 // dictionary<이모티콘, 플레이어 DM 채널>
3. 메인 채널: 게임을 시작한 채널 // 채팅 채널
4. 게임 진행 상태: 현재 게임 진행 단계 // (none, join, start)
5. 정체: 각 플레이어가 맡은 역할 // dictionary<플레이어 DM 채널, 역할>
6. 미션 보드: 이번 게임에서 사용할 미션 보드 // List<숫자>
## 참가
1. 사용 역할: 게임에서 사용하기로 한 추가 역할 //  dictionary<(loyal, evil), 역할>
## 게임 진행
1. 라운드 성공/실패 횟수: 현재까지의 미션 성공/실패 횟수 // 숫자
### 원정대 구성
1. 원정대장: 현재 원정대장을 맡고 있는 플레이어 // 플레이어 DM 채널
2. 원정대원: 원정대장이 지목한 원정대원들 // List<플레이어 DM 채널>
3. 라운드: 몇 번째 원정인가에 대한 트래커 // 숫자
4. 투표현황: 각 플레이어들의 찬반투표 현황 //  dictionary<('찬성', '반대'), 숫자>
### 미션 실행
1. 정체: 각 플레이어가 맡은 역할 // dictionary<플레이어 DM 채널, 역할>
2. 미션현황: 각 플레이어들의 미션선택 현황 //  dictionary<('찬성', '반대'), 숫자>