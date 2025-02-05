# coding:utf8

from Agame.common.common.Packet import Packet


class S2C_ReplyBattleReport(Packet):
	pass


class C2S_CheckBattleResult(Packet):
	pass


class S2C_CheckBattleResult(Packet):
	pass


class C2S_ClientTestBattle(Packet):
	pass


class S2C_ClientTestBattle(Packet):
	pass


class S2C_GetBattleReplay(Packet):
	pass


class C2S_RestartBattle(Packet):
	pass


class S2C_RestartBattle(Packet):
	pass


class C2S_IsBattleFinished(Packet):
	pass


class S2C_IsBattleFinished(Packet):
	pass


class C2G_Login(Packet):
	pass


class G2C_Login(Packet):
	pass


class C2G_Create(Packet):
	pass


class G2C_Create(Packet):
	pass


class C2G_KeepAlive(Packet):
	pass


class G2C_KeepAlive(Packet):
	pass


class C2G_SayHi(Packet):
	pass


class G2C_SayHi(Packet):
	pass


class C2G_Offline(Packet):
	pass


class G2C_Offline(Packet):
	pass


class G2C_Broadcast(Packet):
	pass


class C2G_Activate(Packet):
	pass


class G2C_Activate(Packet):
	pass


class C2G_PingPong(Packet):
	pass


class G2C_PingPong(Packet):
	pass


class C2S_Flush(Packet):
	pass


class S2C_Flush(Packet):
	pass


class S2C_OpObject(Packet):
	pass


class C2S_SyncTime(Packet):
	pass


class S2C_SyncTime(Packet):
	pass


class C2S_SyncProto(Packet):
	pass


class S2C_SyncProto(Packet):
	pass


class S2C_GetAwardNotify(Packet):
	pass


class S2C_FlushUser(Packet):
	pass


class S2C_FlushResource(Packet):
	pass


class S2C_FlushItem(Packet):
	pass


class S2C_FlushRedPoint(Packet):
	pass


class S2C_FlushServerInfo(Packet):
	pass


class S2C_FlushToken(Packet):
	pass


class C2S_GM_Cmd(Packet):
	pass


class S2C_GM_Cmd(Packet):
	pass


class S2C_FlushCharacter(Packet):
	pass


class S2C_FlushFormation(Packet):
	pass


class S2C_FlushEquip(Packet):
	pass


class S2C_FlushTreasureBox(Packet):
	pass


class S2C_FlushMainDungeon(Packet):
	pass


class S2C_FlushHangUp(Packet):
	pass


class S2C_FlushUserGuide(Packet):
	pass


class S2C_FlushUserWorldBoss(Packet):
	pass


class S2C_FlushUserPlayNum(Packet):
	pass


class S2C_FlushUserShare(Packet):
	pass


class S2C_FlushUserArena(Packet):
	pass


class S2C_FlushScoreShop(Packet):
	pass


class S2C_FlushFragment(Packet):
	pass


class S2C_FlushRecruit(Packet):
	pass


class S2C_FlushRecharge(Packet):
	pass


class S2C_FlushInfiniteDungeon(Packet):
	pass


class S2C_FlushUserFriendSystem(Packet):
	pass


class S2C_FlushUserChat(Packet):
	pass


class S2C_FlushUserArtifact(Packet):
	pass


class S2C_FlushUserGuildBoss(Packet):
	pass


class S2C_FlushUserGuild(Packet):
	pass


class S2C_FlushBattlePass(Packet):
	pass


class S2C_FlushUserCasualGame(Packet):
	pass


class S2C_FlushUserMow(Packet):
	pass


class S2C_FlushDailySpecials(Packet):
	pass


class S2C_FlushUserFund(Packet):
	pass


class S2C_FlushActivityOpen(Packet):
	pass


class S2C_FlushFirstRecharge(Packet):
	pass


class S2C_FlushAccumulatedRecharge(Packet):
	pass


class S2C_FlushMonthlyCard(Packet):
	pass


class S2C_FlushAvatar(Packet):
	pass


class S2C_FlushUserDailySign(Packet):
	pass


class S2C_FlushUserPushGift(Packet):
	pass


class S2C_FlushUserSevenSign(Packet):
	pass


class S2C_FlushSevenAct(Packet):
	pass


class S2C_FlushAchievement(Packet):
	pass


class S2C_FlushUserPrivilege(Packet):
	pass


class S2C_FlushBack(Packet):
	pass


class S2C_FlushUserBack(Packet):
	pass


class S2C_FlushUserTower(Packet):
	pass


class S2C_FlushCompanionBook(Packet):
	pass


class S2C_FlushHonor(Packet):
	pass


class S2C_FlushUserSeriesGift(Packet):
	pass


class S2C_FlushUserDailySurpriseBenefit(Packet):
	pass


class S2C_FlushUserFunctionPreview(Packet):
	pass


class S2C_FlushDress(Packet):
	pass


class S2C_FlushUserTreasury(Packet):
	pass


class S2C_FlushAdvertise(Packet):
	pass


class S2C_FlushQuestionnaire(Packet):
	pass


class C2S_GetRedPointUpdateInfo(Packet):
	pass


class S2C_GetRedPointUpdateInfo(Packet):
	pass


class S2C_FlushShortBattlePass(Packet):
	pass


class S2C_FlushThemeActivity(Packet):
	pass


class S2C_FlushCompanionEquipment(Packet):
	pass


class S2C_FlushCompanionEquipmentFormation(Packet):
	pass


class S2C_FlushCloseFunction(Packet):
	pass


class S2C_FlushInitTime(Packet):
	pass


class S2C_FlushPet(Packet):
	pass


class S2C_FlushPeakArenaActivity(Packet):
	pass


class S2C_FlushPack(Packet):
	pass


class S2C_FlushUnBlock(Packet):
	pass


class S2C_FlushGoblin(Packet):
	pass


class S2C_FlushSelectGift(Packet):
	pass


class S2C_FlushAlchemy(Packet):
	pass


class S2C_FlushPiggyBank(Packet):
	pass


class S2C_FlushGuildGvg(Packet):
	pass


class C2S_Test_OpManager(Packet):
	pass


class S2C_Test_OpManager(Packet):
	pass


class C2S_Test_PVEBattleBegin(Packet):
	pass


class S2C_Test_PVEBattleBegin(Packet):
	pass


class S2C_Test_PVEBattleFinish(Packet):
	pass


class C2S_Test_PVPBattleBegin(Packet):
	pass


class S2C_Test_PVPBattleBegin(Packet):
	pass


class S2C_Test_PVPBattleFinish(Packet):
	pass


class C2S_CommonRank_GetList(Packet):
	pass


class S2C_CommonRank_GetList(Packet):
	pass


class C2S_FirstRecord_GetInfo(Packet):
	pass


class S2C_FirstRecord_GetInfo(Packet):
	pass


class S2C_FirstRecord_Notify(Packet):
	pass


class S2C_User_NotifyKickOut(Packet):
	pass


class C2S_UserInfo_ModifyName(Packet):
	pass


class S2C_UserInfo_ModifyName(Packet):
	pass


class C2S_UserInfo_GetDetail(Packet):
	pass


class S2C_UserInfo_GetDetail(Packet):
	pass


class S2C_AdultCheck_Warning(Packet):
	pass


class C2S_CommonAction_Trigger(Packet):
	pass


class S2C_CommonAction_Trigger(Packet):
	pass


class C2S_Item_Use(Packet):
	pass


class S2C_Item_Use(Packet):
	pass


class C2S_Diamond_Exchange(Packet):
	pass


class S2C_Diamond_Exchange(Packet):
	pass


class C2S_AccountBindAward(Packet):
	pass


class S2C_AccountBindAward(Packet):
	pass


class S2C_CloseFunctionNtf(Packet):
	pass


class C2S_CommunityFollowAward(Packet):
	pass


class S2C_CommunityFollowAward(Packet):
	pass


class S2C_UnBlockNtf(Packet):
	pass


class S2C_API_GetRoleList(Packet):
	pass


class S2C_API_SearchUser(Packet):
	pass


class C2S_Log_OpenPanel(Packet):
	pass


class S2C_Log_OpenPanel(Packet):
	pass


class C2S_TreasureBox_Open(Packet):
	pass


class S2C_TreasureBox_Open(Packet):
	pass


class C2S_TreasureBox_SetAutoOpenCondition(Packet):
	pass


class S2C_TreasureBox_SetAutoOpenCondition(Packet):
	pass


class C2S_TreasureBox_Upgrade(Packet):
	pass


class S2C_TreasureBox_Upgrade(Packet):
	pass


class C2S_TreasureBox_ItemUpSpeedTime(Packet):
	pass


class S2C_TreasureBox_ItemUpSpeedTime(Packet):
	pass


class C2S_TreasureBox_AdvertiseUpSpeedTime(Packet):
	pass


class S2C_TreasureBox_AdvertiseUpSpeedTime(Packet):
	pass


class C2S_TreasureBox_AutoOpen(Packet):
	pass


class S2C_TreasureBox_AutoOpen(Packet):
	pass


class C2S_TreasureBox_BuyUpgradeCnt(Packet):
	pass


class S2C_TreasureBox_BuyUpgradeCnt(Packet):
	pass


class C2S_TreasureBox_ChestUpgradeFinish(Packet):
	pass


class S2C_TreasureBox_ChestUpgradeFinish(Packet):
	pass


class C2S_HangUp_ObtainAwards(Packet):
	pass


class S2C_HangUp_ObtainAwards(Packet):
	pass


class C2S_HangUp_UseItemObtainAwards(Packet):
	pass


class S2C_HangUp_UseItemObtainAwards(Packet):
	pass


class S2C_QuestMain_Flush(Packet):
	pass


class C2S_QuestMain_GetReward(Packet):
	pass


class S2C_QuestMain_GetReward(Packet):
	pass


class C2S_MainDungeon_ChallengeBegin(Packet):
	pass


class S2C_MainDungeon_ChallengeBegin(Packet):
	pass


class S2C_MainDungeon_ChallengeFinish(Packet):
	pass


class C2S_MainDungeon_ObtainAward(Packet):
	pass


class S2C_MainDungeon_ObtainAward(Packet):
	pass


class C2S_MainDungeon_GetStageRecordInfo(Packet):
	pass


class S2C_MainDungeon_GetStageRecordInfo(Packet):
	pass


class C2S_MainDungeon_OnekeyObtainChapterStageRewards(Packet):
	pass


class S2C_MainDungeon_OnekeyObtainChapterStageRewards(Packet):
	pass


class C2S_MainDungeon_ObtainChapterRewards(Packet):
	pass


class S2C_MainDungeon_ObtainChapterRewards(Packet):
	pass


class C2S_MainDungeon_SweepLastLevel(Packet):
	pass


class S2C_MainDungeon_SweepLastLevel(Packet):
	pass


class C2S_Equipment_Wear(Packet):
	pass


class S2C_Equipment_Wear(Packet):
	pass


class C2S_Equipment_Sale(Packet):
	pass


class S2C_Equipment_Sale(Packet):
	pass


class C2S_Equipment_Illusion(Packet):
	pass


class S2C_Equipment_Illusion(Packet):
	pass


class C2S_Equipment_ManualSale(Packet):
	pass


class S2C_Equipment_ManualSale(Packet):
	pass


class C2S_Mail_Info(Packet):
	pass


class S2C_Mail_Info(Packet):
	pass


class C2S_Mail_Award(Packet):
	pass


class S2C_Mail_Award(Packet):
	pass


class C2S_Mail_Del(Packet):
	pass


class S2C_Mail_Del(Packet):
	pass


class C2S_Mail_Read(Packet):
	pass


class S2C_Mail_Read(Packet):
	pass


class S2C_Mail_New(Packet):
	pass


class C2S_SkillTree_Upgrade(Packet):
	pass


class S2C_SkillTree_Upgrade(Packet):
	pass


class C2S_MainCharacter_Switch(Packet):
	pass


class S2C_MainCharacter_Switch(Packet):
	pass


class C2S_Guide_BattleRecord(Packet):
	pass


class S2C_Guide_BattleRecord(Packet):
	pass


class C2S_Guide_SaveRecord(Packet):
	pass


class S2C_Guide_SaveRecord(Packet):
	pass


class C2S_WorldBoss_RespawnBoss(Packet):
	pass


class S2C_WorldBoss_RespawnBoss(Packet):
	pass


class C2S_WorldBoss_ChallengeBegin(Packet):
	pass


class S2C_WorldBoss_ChallengeBegin(Packet):
	pass


class S2C_WorldBoss_ChallengeFinish(Packet):
	pass


class C2S_PlayNum_BuyCnt(Packet):
	pass


class S2C_PlayNum_BuyCnt(Packet):
	pass


class C2S_Formation_Upgrade(Packet):
	pass


class S2C_Formation_Upgrade(Packet):
	pass


class C2S_Formation_Save(Packet):
	pass


class S2C_Formation_Save(Packet):
	pass


class C2S_Formation_SaveTeam(Packet):
	pass


class S2C_Formation_SaveTeam(Packet):
	pass


class C2S_Formation_RenameTeam(Packet):
	pass


class S2C_Formation_RenameTeam(Packet):
	pass


class C2S_Formation_Get(Packet):
	pass


class S2C_Formation_Get(Packet):
	pass


class S2C_FlushCharacterFormationSlot(Packet):
	pass


class C2S_Formation_GetTeam(Packet):
	pass


class S2C_Formation_GetTeam(Packet):
	pass


class C2S_CharacterCompanion_UpgradeQuality(Packet):
	pass


class S2C_CharacterCompanion_UpgradeQuality(Packet):
	pass


class C2S_Arena_MatchOpponent(Packet):
	pass


class S2C_Arena_MatchOpponent(Packet):
	pass


class C2S_Arena_Like(Packet):
	pass


class S2C_Arena_Like(Packet):
	pass


class C2S_Arena_Enter(Packet):
	pass


class S2C_Arena_Enter(Packet):
	pass


class C2S_Arena_ChallengeBegin(Packet):
	pass


class S2C_Arena_ChallengeBegin(Packet):
	pass


class S2C_Arena_ChallengeFinish(Packet):
	pass


class C2S_Arena_GetScoreRank(Packet):
	pass


class S2C_Arena_GetScoreRank(Packet):
	pass


class C2S_Arena_GetBattleRecord(Packet):
	pass


class S2C_Arena_GetBattleRecord(Packet):
	pass


class C2S_Arena_GetTaskAward(Packet):
	pass


class S2C_Arena_GetTaskAward(Packet):
	pass


class C2S_Arena_OneKeyGetTaskAward(Packet):
	pass


class S2C_Arena_OneKeyGetTaskAward(Packet):
	pass


class C2S_Arena_SetDefendFormation(Packet):
	pass


class S2C_Arena_SetDefendFormation(Packet):
	pass


class S2C_Arena_NotifyAttacked(Packet):
	pass


class C2S_ScoreShop_Buy(Packet):
	pass


class S2C_ScoreShop_Buy(Packet):
	pass


class C2S_ScoreShop_GetRefreshShop(Packet):
	pass


class S2C_ScoreShop_GetRefreshShop(Packet):
	pass


class C2S_Share_Award(Packet):
	pass


class S2C_Share_Award(Packet):
	pass


class C2S_Recruit_Roll(Packet):
	pass


class S2C_Recruit_Roll(Packet):
	pass


class C2S_Recruit_AwardExtra(Packet):
	pass


class S2C_Recruit_AwardExtra(Packet):
	pass


class C2S_Fragment_Compose(Packet):
	pass


class S2C_Fragment_Compose(Packet):
	pass


class S2C_FlushUserAction(Packet):
	pass


class C2S_InfiniteDungeon_ChallengeBegin(Packet):
	pass


class S2C_InfiniteDungeon_ChallengeBegin(Packet):
	pass


class S2C_InfiniteDungeon_ChallengeFinish(Packet):
	pass


class C2S_InfiniteDungeon_GetStageRecordInfo(Packet):
	pass


class S2C_InfiniteDungeon_GetStageRecordInfo(Packet):
	pass


class C2S_InfiniteDungeon_AwardHangup(Packet):
	pass


class S2C_InfiniteDungeon_AwardHangup(Packet):
	pass


class C2S_InfiniteDungeon_StartHangup(Packet):
	pass


class S2C_InfiniteDungeon_StartHangup(Packet):
	pass


class C2S_Friend_Apply(Packet):
	pass


class S2C_Friend_Apply(Packet):
	pass


class C2S_Friend_Ack(Packet):
	pass


class S2C_Friend_Ack(Packet):
	pass


class C2S_Friend_Search(Packet):
	pass


class S2C_Friend_Search(Packet):
	pass


class C2S_Friend_Recommend(Packet):
	pass


class S2C_Friend_Recommend(Packet):
	pass


class C2S_Friend_DelFriend(Packet):
	pass


class S2C_Friend_DelFriend(Packet):
	pass


class C2S_Friend_AddBlack(Packet):
	pass


class S2C_Friend_AddBlack(Packet):
	pass


class C2S_Friend_DelBlack(Packet):
	pass


class S2C_Friend_DelBlack(Packet):
	pass


class C2S_Friend_GiveGift(Packet):
	pass


class S2C_Friend_GiveGift(Packet):
	pass


class C2S_Friend_AcceptGift(Packet):
	pass


class S2C_Friend_AcceptGift(Packet):
	pass


class S2C_Friend_NotifyApply(Packet):
	pass


class S2C_Friend_NotifyAck(Packet):
	pass


class S2C_Friend_NotifyDelFriend(Packet):
	pass


class S2C_Friend_NotifyGiveGift(Packet):
	pass


class S2C_Friend_NotifyAddBlack(Packet):
	pass


class C2S_Friend_BatchApply(Packet):
	pass


class S2C_Friend_BatchApply(Packet):
	pass


class C2S_Friend_BatchGiveGift(Packet):
	pass


class S2C_Friend_BatchGiveGift(Packet):
	pass


class C2S_Friend_BatchAcceptGift(Packet):
	pass


class S2C_Friend_BatchAcceptGift(Packet):
	pass


class C2S_Friend_BatchAck(Packet):
	pass


class S2C_Friend_BatchAck(Packet):
	pass


class C2S_Chat_Content(Packet):
	pass


class S2C_Chat_Content(Packet):
	pass


class S2C_Chat_Notify_Content(Packet):
	pass


class S2C_Chat_Notify_System(Packet):
	pass


class S2C_Chat_SetForbidPrivate(Packet):
	pass


class C2S_Chat_SetForbidPrivate(Packet):
	pass


class C2S_Chat_GetForbidPrivate(Packet):
	pass


class S2C_Chat_GetForbidPrivate(Packet):
	pass


class S2C_Chat_Notify_GuildSystem(Packet):
	pass


class C2S_Chat_GetInfos(Packet):
	pass


class S2C_Chat_GetInfos(Packet):
	pass


class C2S_Chat_GetSystemInfos(Packet):
	pass


class S2C_Chat_GetSystemInfos(Packet):
	pass


class C2S_Chat_DeleteFriendChat(Packet):
	pass


class S2C_Chat_DeleteFriendChat(Packet):
	pass


class C2S_Chat_SetLatestReadTm(Packet):
	pass


class S2C_Chat_SetLatestReadTm(Packet):
	pass


class S2C_Recharge_NotifySuccess(Packet):
	pass


class C2S_Artifact_UpLevel(Packet):
	pass


class S2C_Artifact_UpLevel(Packet):
	pass


class C2S_Artifact_UpStar(Packet):
	pass


class S2C_Artifact_UpStar(Packet):
	pass


class C2S_Artifact_Compose_Active(Packet):
	pass


class S2C_Artifact_Compose_Active(Packet):
	pass


class C2S_Artifact_Compose_UpLevel(Packet):
	pass


class S2C_Artifact_Compose_UpLevel(Packet):
	pass


class C2S_Artifact_Equip(Packet):
	pass


class S2C_Artifact_Equip(Packet):
	pass


class C2S_Artifact_Equip_OneKey(Packet):
	pass


class S2C_Artifact_Equip_OneKey(Packet):
	pass


class C2S_Artifact_Compose_ActiveAndUpLevel(Packet):
	pass


class S2C_Artifact_Compose_ActiveAndUpLevel(Packet):
	pass


class C2S_GuildBoss_ChallengeBegin(Packet):
	pass


class S2C_GuildBoss_ChallengeBegin(Packet):
	pass


class S2C_GuildBoss_ChallengeFinish(Packet):
	pass


class C2S_GuildBoss_GetRank(Packet):
	pass


class S2C_GuildBoss_GetRank(Packet):
	pass


class C2S_Guild_Create(Packet):
	pass


class S2C_Guild_Create(Packet):
	pass


class C2S_Guild_Join(Packet):
	pass


class S2C_Guild_Join(Packet):
	pass


class C2S_Guild_Quit(Packet):
	pass


class S2C_Guild_Quit(Packet):
	pass


class C2S_Guild_FastJoin(Packet):
	pass


class S2C_Guild_FastJoin(Packet):
	pass


class C2S_Guild_EditName(Packet):
	pass


class S2C_Guild_EditName(Packet):
	pass


class C2S_Guild_SetUpgradeStrategy(Packet):
	pass


class S2C_Guild_SetUpgradeStrategy(Packet):
	pass


class C2S_Guild_ObtainTaskReward(Packet):
	pass


class S2C_Guild_ObtainTaskReward(Packet):
	pass


class C2S_Guild_ObtainQuestReward(Packet):
	pass


class S2C_Guild_ObtainQuestReward(Packet):
	pass


class C2S_Guild_GetQuestInfo(Packet):
	pass


class S2C_Guild_GetQuestInfo(Packet):
	pass


class C2S_Guild_AssignTitle(Packet):
	pass


class S2C_Guild_AssignTitle(Packet):
	pass


class C2S_Guild_Kick(Packet):
	pass


class S2C_Guild_Kick(Packet):
	pass


class C2S_Guild_InGuild(Packet):
	pass


class S2C_Guild_InGuild(Packet):
	pass


class C2S_Guild_DailySign(Packet):
	pass


class S2C_Guild_DailySign(Packet):
	pass


class C2S_Guild_LearnTech(Packet):
	pass


class S2C_Guild_LearnTech(Packet):
	pass


class C2S_Guild_Search(Packet):
	pass


class S2C_Guild_Search(Packet):
	pass


class C2S_Guild_Approve(Packet):
	pass


class S2C_Guild_Approve(Packet):
	pass


class C2S_Guild_UpspeedTech(Packet):
	pass


class S2C_Guild_UpspeedTech(Packet):
	pass


class C2S_Guild_Recommend(Packet):
	pass


class S2C_Guild_Recommend(Packet):
	pass


class C2S_Guild_GetGuildInfo(Packet):
	pass


class S2C_Guild_GetGuildInfo(Packet):
	pass


class C2S_Guild_Attorn(Packet):
	pass


class S2C_Guild_Attorn(Packet):
	pass


class C2S_Guild_SetInfo(Packet):
	pass


class S2C_Guild_SetInfo(Packet):
	pass


class C2S_Guild_OnekeyObtainQuestReward(Packet):
	pass


class S2C_Guild_OnekeyObtainQuestReward(Packet):
	pass


class C2S_Guild_SetAnnounce(Packet):
	pass


class S2C_Guild_SetAnnounce(Packet):
	pass


class C2S_Guild_CancelTechUpgrade(Packet):
	pass


class S2C_Guild_CancelTechUpgrade(Packet):
	pass


class C2S_Guild_AssistOther(Packet):
	pass


class S2C_Guild_AssistOther(Packet):
	pass


class C2S_Guild_ReqAssist(Packet):
	pass


class S2C_Guild_ReqAssist(Packet):
	pass


class C2S_Guild_GetAssistInfo(Packet):
	pass


class S2C_Guild_GetAssistInfo(Packet):
	pass


class S2C_Guild_NotifyDismiss(Packet):
	pass


class S2C_Guild_NotifyJoin(Packet):
	pass


class S2C_Guild_NotifyQuit(Packet):
	pass


class S2C_Guild_NotifyUserOnline(Packet):
	pass


class S2C_Guild_NotifyEditName(Packet):
	pass


class S2C_Guild_NotifySetUpgradeStrategy(Packet):
	pass


class S2C_Guild_NotifyLearnTech(Packet):
	pass


class S2C_Guild_NotifyUpspeedTech(Packet):
	pass


class S2C_Guild_NotifySignRecord(Packet):
	pass


class S2C_Guild_NotifyAssignTitle(Packet):
	pass


class S2C_Guild_NotifyKick(Packet):
	pass


class S2C_Guild_NotifyApplyJoin(Packet):
	pass


class S2C_Guild_NotifyDeleteApply(Packet):
	pass


class S2C_Guild_NotifyGuildResourceOp(Packet):
	pass


class S2C_Guild_NotifyAttorn(Packet):
	pass


class S2C_Guild_NotifySetInfo(Packet):
	pass


class S2C_Guild_NotifySetAnnounce(Packet):
	pass


class S2C_Guild_NotifyApprove(Packet):
	pass


class S2C_Guild_NotifyGuildLog(Packet):
	pass


class S2C_Guild_NotifyUserOffline(Packet):
	pass


class S2C_Guild_NotifyCancelTech(Packet):
	pass


class S2C_Guild_NotifyAssistMe(Packet):
	pass


class S2C_Guild_NotifyReqAssist(Packet):
	pass


class S2C_Guild_NotifyUserGuildWeeklyData(Packet):
	pass


class C2S_Guild_GetDetail(Packet):
	pass


class S2C_Guild_GetDetail(Packet):
	pass


class C2S_Guild_GetSignAward(Packet):
	pass


class S2C_Guild_GetSignAward(Packet):
	pass


class C2S_Guild_SendMail(Packet):
	pass


class S2C_Guild_SendMail(Packet):
	pass


class C2S_Guild_GetGuildList(Packet):
	pass


class S2C_Guild_GetGuildList(Packet):
	pass


class C2S_Rogue_GetInfo(Packet):
	pass


class S2C_Rogue_GetInfo(Packet):
	pass


class C2S_Rogue_SelectDifficulty(Packet):
	pass


class S2C_Rogue_SelectDifficulty(Packet):
	pass


class C2S_Rogue_SelectCharacter(Packet):
	pass


class S2C_Rogue_SelectCharacter(Packet):
	pass


class C2S_Rogue_EnterGrid(Packet):
	pass


class S2C_Rogue_EnterGrid(Packet):
	pass


class C2S_Rogue_ChallengeBegin(Packet):
	pass


class S2C_Rogue_ChallengeBegin(Packet):
	pass


class C2S_Rogue_Try(Packet):
	pass


class S2C_Rogue_Try(Packet):
	pass


class C2S_Rogue_UseItem(Packet):
	pass


class S2C_Rogue_UseItem(Packet):
	pass


class C2S_Rogue_SelectAward(Packet):
	pass


class S2C_Rogue_SelectAward(Packet):
	pass


class C2S_Rogue_FlushShop(Packet):
	pass


class S2C_Rogue_FlushShop(Packet):
	pass


class C2S_Rogue_BuyShop(Packet):
	pass


class S2C_Rogue_BuyShop(Packet):
	pass


class C2S_Rogue_Recruit(Packet):
	pass


class S2C_Rogue_Recruit(Packet):
	pass


class C2S_Rogue_Wish(Packet):
	pass


class S2C_Rogue_Wish(Packet):
	pass


class C2S_Rogue_RecruitSelect(Packet):
	pass


class S2C_Rogue_RecruitSelect(Packet):
	pass


class C2S_Rogue_UseDevice(Packet):
	pass


class S2C_Rogue_UseDevice(Packet):
	pass


class C2S_Rogue_ActiveTree(Packet):
	pass


class S2C_Rogue_ActiveTree(Packet):
	pass


class C2S_Rogue_TaskAward(Packet):
	pass


class S2C_Rogue_TaskAward(Packet):
	pass


class C2S_Rogue_BookAward(Packet):
	pass


class S2C_Rogue_BookAward(Packet):
	pass


class C2S_Rogue_Quit(Packet):
	pass


class S2C_Rogue_Quit(Packet):
	pass


class S2C_Rogue_ChallengeFinish(Packet):
	pass


class S2C_Rogue_SyncInnerInfo(Packet):
	pass


class C2S_Rogue_UseSpring(Packet):
	pass


class S2C_Rogue_UseSpring(Packet):
	pass


class C2S_Rogue_DiscardResource(Packet):
	pass


class S2C_Rogue_DiscardResource(Packet):
	pass


class S2C_Rogue_SyncBook(Packet):
	pass


class C2S_Rogue_RetryChallenge(Packet):
	pass


class S2C_Rogue_RetryChallenge(Packet):
	pass


class S2C_Rogue_TriggerEvent(Packet):
	pass


class S2C_Rogue_TriggerEventResource(Packet):
	pass


class C2S_DailyQuest_AwardQuest(Packet):
	pass


class S2C_DailyQuest_AwardQuest(Packet):
	pass


class C2S_DailyQuest_AwardActive(Packet):
	pass


class S2C_DailyQuest_AwardActive(Packet):
	pass


class S2C_BattlePass_BuyNtf(Packet):
	pass


class C2S_BattlePass_AwardLv(Packet):
	pass


class S2C_BattlePass_AwardLv(Packet):
	pass


class C2S_BattlePass_BuyLv(Packet):
	pass


class S2C_BattlePass_BuyLv(Packet):
	pass


class C2S_BattlePass_AwardQuest(Packet):
	pass


class S2C_BattlePass_AwardQuest(Packet):
	pass


class C2S_Rogue_GetFirstAward(Packet):
	pass


class S2C_Rogue_GetFirstAward(Packet):
	pass


class C2S_CasualGame_EnterGame(Packet):
	pass


class S2C_CasualGame_EnterGame(Packet):
	pass


class S2C_CasualGame_NotifyPlayCnt(Packet):
	pass


class C2S_CasualGame_FinishGame(Packet):
	pass


class S2C_CasualGame_FinishGame(Packet):
	pass


class C2S_Mow_BeginMow(Packet):
	pass


class S2C_Mow_BeginMow(Packet):
	pass


class C2S_Mow_FinishMow(Packet):
	pass


class S2C_Mow_FinishMow(Packet):
	pass


class C2S_Mow_Sweep(Packet):
	pass


class S2C_Mow_Sweep(Packet):
	pass


class C2S_DailySpecials_Award(Packet):
	pass


class S2C_DailySpecials_Award(Packet):
	pass


class S2C_DailySpecials_BuyNtf(Packet):
	pass


class S2C_DailySpecials_ContinueBuyNtf(Packet):
	pass


class C2S_Fund_OnekeyObtainReward(Packet):
	pass


class S2C_Fund_OnekeyObtainReward(Packet):
	pass


class C2S_Fund_ObtainReward(Packet):
	pass


class S2C_Fund_ObtainReward(Packet):
	pass


class C2S_FirstRecharge_Award(Packet):
	pass


class S2C_FirstRecharge_Award(Packet):
	pass


class S2C_FirstRecharge_BuyNtf(Packet):
	pass


class C2S_AccumulatedRecharge_Award(Packet):
	pass


class S2C_AccumulatedRecharge_Award(Packet):
	pass


class C2S_MonthlyCard_DailyAward(Packet):
	pass


class S2C_MonthlyCard_DailyAward(Packet):
	pass


class S2C_MonthlyCard_BuyNtf(Packet):
	pass


class C2S_Avatar_Set(Packet):
	pass


class S2C_Avatar_Set(Packet):
	pass


class C2S_Avatar_Frame_Set(Packet):
	pass


class S2C_Avatar_Frame_Set(Packet):
	pass


class C2S_DailySign_ObtainReward(Packet):
	pass


class S2C_DailySign_ObtainReward(Packet):
	pass


class C2S_PushGift_Buy(Packet):
	pass


class S2C_PushGift_Buy(Packet):
	pass


class S2C_PushGift_NotifyTrigger(Packet):
	pass


class C2S_SevenSign_Award(Packet):
	pass


class S2C_SevenSign_Award(Packet):
	pass


class C2S_Achievement_Award(Packet):
	pass


class S2C_Achievement_Award(Packet):
	pass


class S2C_Achievement_Notify(Packet):
	pass


class C2S_SevenAct_AwardPoint(Packet):
	pass


class S2C_SevenAct_AwardPoint(Packet):
	pass


class C2S_SevenAct_AwardQuest(Packet):
	pass


class S2C_SevenAct_AwardQuest(Packet):
	pass


class C2S_Back_Decompose(Packet):
	pass


class S2C_Back_Decompose(Packet):
	pass


class C2S_Back_Lock(Packet):
	pass


class S2C_Back_Lock(Packet):
	pass


class C2S_Back_UpgradeLv(Packet):
	pass


class S2C_Back_UpgradeLv(Packet):
	pass


class C2S_Back_UpgradeStar(Packet):
	pass


class S2C_Back_UpgradeStar(Packet):
	pass


class C2S_Back_Refresh(Packet):
	pass


class S2C_Back_Refresh(Packet):
	pass


class C2S_Back_Buy(Packet):
	pass


class S2C_Back_Buy(Packet):
	pass


class C2S_Back_SetWish(Packet):
	pass


class S2C_Back_SetWish(Packet):
	pass


class C2S_Back_ExpandBag(Packet):
	pass


class S2C_Back_ExpandBag(Packet):
	pass


class C2S_Back_UpgradeBook(Packet):
	pass


class S2C_Back_UpgradeBook(Packet):
	pass


class C2S_Tower_ChallengeBegin(Packet):
	pass


class S2C_Tower_ChallengeBegin(Packet):
	pass


class S2C_Tower_ChallengeFinish(Packet):
	pass


class C2S_Tower_ObtainGlobalFirstPassRewards(Packet):
	pass


class S2C_Tower_ObtainGlobalFirstPassRewards(Packet):
	pass


class C2S_Tower_FastSweep(Packet):
	pass


class S2C_Tower_FastSweep(Packet):
	pass


class C2S_Tower_UnlockBuffSlot(Packet):
	pass


class S2C_Tower_UnlockBuffSlot(Packet):
	pass


class C2S_Tower_RefreshBuff(Packet):
	pass


class S2C_Tower_RefreshBuff(Packet):
	pass


class C2S_Tower_SelectBuff(Packet):
	pass


class S2C_Tower_SelectBuff(Packet):
	pass


class C2S_Tower_SetBuffPefer(Packet):
	pass


class S2C_Tower_SetBuffPefer(Packet):
	pass


class S2C_Tower_NotifyServerMaxId(Packet):
	pass


class C2S_Tower_GetUserByFloors(Packet):
	pass


class S2C_Tower_GetUserByFloors(Packet):
	pass


class C2S_Tower_GetInfo(Packet):
	pass


class S2C_Tower_GetInfo(Packet):
	pass


class C2S_CompanionBook_UpgradeLv(Packet):
	pass


class S2C_CompanionBook_UpgradeLv(Packet):
	pass


class C2S_Honor_AwardQuest(Packet):
	pass


class S2C_Honor_AwardQuest(Packet):
	pass


class C2S_Honor_Upgrade(Packet):
	pass


class S2C_Honor_Upgrade(Packet):
	pass


class C2S_SeriesGift_Buy(Packet):
	pass


class S2C_SeriesGift_Buy(Packet):
	pass


class S2C_SeriesGift_NotifyTrigger(Packet):
	pass


class C2S_DailySurpriseBenefit_ObtainRewards(Packet):
	pass


class S2C_DailySurpriseBenefit_ObtainRewards(Packet):
	pass


class C2S_FunctionPreview_ObtainRewards(Packet):
	pass


class S2C_FunctionPreview_ObtainRewards(Packet):
	pass


class C2S_Treasury_ChallengeBegin(Packet):
	pass


class S2C_Treasury_ChallengeBegin(Packet):
	pass


class S2C_Treasury_ChallengeFinish(Packet):
	pass


class C2S_Treasury_Sweep(Packet):
	pass


class S2C_Treasury_Sweep(Packet):
	pass


class C2S_Advertise_Use(Packet):
	pass


class S2C_Advertise_Use(Packet):
	pass


class C2S_GiftCode_Award(Packet):
	pass


class S2C_GiftCode_Award(Packet):
	pass


class C2S_ShortBattlePass_Start(Packet):
	pass


class S2C_ShortBattlePass_Start(Packet):
	pass


class C2S_ShortBattlePass_AwardBp(Packet):
	pass


class S2C_ShortBattlePass_AwardBp(Packet):
	pass


class S2C_ShortBattlePass_BuyBpNtf(Packet):
	pass


class C2S_ShortBattlePass_AwardQuest(Packet):
	pass


class S2C_ShortBattlePass_AwardQuest(Packet):
	pass


class C2S_ShortBattlePass_AwardPack(Packet):
	pass


class S2C_ShortBattlePass_AwardPack(Packet):
	pass


class S2C_ShortBattlePass_BuyPackNtf(Packet):
	pass


class C2S_ShortBattlePass_AwardProgress(Packet):
	pass


class S2C_ShortBattlePass_AwardProgress(Packet):
	pass


class S2C_ThemeActivity_Notify(Packet):
	pass


class C2S_ThemeActivity_Roll(Packet):
	pass


class S2C_ThemeActivity_Roll(Packet):
	pass


class C2S_ThemeActivity_Scrape(Packet):
	pass


class S2C_ThemeActivity_Scrape(Packet):
	pass


class C2S_ThemeActivity_AwardAccRoll(Packet):
	pass


class S2C_ThemeActivity_AwardAccRoll(Packet):
	pass


class S2C_ThemeActivity_BuyPackNtf(Packet):
	pass


class C2S_ThemeActivity_AwardQuest(Packet):
	pass


class S2C_ThemeActivity_AwardQuest(Packet):
	pass


class C2S_ThemeActivity_NewLottery(Packet):
	pass


class S2C_ThemeActivity_NewLottery(Packet):
	pass


class C2S_ThemeActivity_AwardPack(Packet):
	pass


class S2C_ThemeActivity_AwardPack(Packet):
	pass


class C2S_ThemeActivity_SetWish(Packet):
	pass


class S2C_ThemeActivity_SetWish(Packet):
	pass


class C2S_Territory_GetInfo(Packet):
	pass


class S2C_Territory_GetInfo(Packet):
	pass


class C2S_Territory_UpgradeMainCity(Packet):
	pass


class S2C_Territory_UpgradeMainCity(Packet):
	pass


class C2S_Territory_RefreshTradeArea(Packet):
	pass


class S2C_Territory_RefreshTradeArea(Packet):
	pass


class C2S_Territory_TradeDispatch(Packet):
	pass


class S2C_Territory_TradeDispatch(Packet):
	pass


class C2S_Territory_AutoTradeDispatch(Packet):
	pass


class S2C_Territory_AutoTradeDispatch(Packet):
	pass


class C2S_Territory_ObtainTradeDispatchRewards(Packet):
	pass


class S2C_Territory_ObtainTradeDispatchRewards(Packet):
	pass


class C2S_Territory_UpgradeBuilding(Packet):
	pass


class S2C_Territory_UpgradeBuilding(Packet):
	pass


class C2S_Territory_ObtainBuildingReward(Packet):
	pass


class S2C_Territory_ObtainBuildingReward(Packet):
	pass


class C2S_Territory_ObtainBuildingRewardsUseItem(Packet):
	pass


class S2C_Territory_ObtainBuildingRewardsUseItem(Packet):
	pass


class C2S_Territory_VisitFriend(Packet):
	pass


class S2C_Territory_VisitFriend(Packet):
	pass


class S2C_Territory_NotifyLog(Packet):
	pass


class C2S_Territory_Like(Packet):
	pass


class S2C_Territory_Like(Packet):
	pass


class S2C_Territory_NotifyLike(Packet):
	pass


class C2S_Territory_ObtainEventRewards(Packet):
	pass


class S2C_Territory_ObtainEventRewards(Packet):
	pass


class C2S_Territory_ObtainFriendEventRewards(Packet):
	pass


class S2C_Territory_ObtainFriendEventRewards(Packet):
	pass


class C2S_Territory_ObtainQuestRewards(Packet):
	pass


class S2C_Territory_ObtainQuestRewards(Packet):
	pass


class S2C_Territory_NotifyEventAssignFriend(Packet):
	pass


class C2S_Territory_ObtainRewardsByAdv(Packet):
	pass


class S2C_Territory_ObtainRewardsByAdv(Packet):
	pass


class C2S_Territory_CompanionEquip(Packet):
	pass


class S2C_Territory_CompanionEquip(Packet):
	pass


class C2S_CompanionEquip_ChangeFormation(Packet):
	pass


class S2C_CompanionEquip_ChangeFormation(Packet):
	pass


class C2S_CompanionEquip_Upgrade(Packet):
	pass


class S2C_CompanionEquip_Upgrade(Packet):
	pass


class C2S_CompanionEquip_Forge(Packet):
	pass


class S2C_CompanionEquip_Forge(Packet):
	pass


class C2S_CompanionEquip_Decompose(Packet):
	pass


class S2C_CompanionEquip_Decompose(Packet):
	pass


class C2S_CompanionEquip_Combine(Packet):
	pass


class S2C_CompanionEquip_Combine(Packet):
	pass


class C2S_CompanionEquip_Lock(Packet):
	pass


class S2C_CompanionEquip_Lock(Packet):
	pass


class C2S_GuildGVE_ChallengeBegin(Packet):
	pass


class S2C_GuildGVE_ChallengeBegin(Packet):
	pass


class S2C_GuildGVE_ChallengeFinish(Packet):
	pass


class C2S_GuildGVE_GetRank(Packet):
	pass


class S2C_GuildGVE_GetRank(Packet):
	pass


class C2S_GuildGVE_GetGiveLog(Packet):
	pass


class S2C_GuildGVE_GetGiveLog(Packet):
	pass


class C2S_GuildGVE_Give(Packet):
	pass


class S2C_GuildGVE_Give(Packet):
	pass


class S2C_GuildGVE_GiveNtf(Packet):
	pass


class C2S_GuildGVE_BoxAward(Packet):
	pass


class S2C_GuildGVE_BoxAward(Packet):
	pass


class C2S_GuildGVE_StartAddition(Packet):
	pass


class S2C_GuildGVE_StartAddition(Packet):
	pass


class C2S_GuildGVE_GetInfo(Packet):
	pass


class S2C_GuildGVE_GetInfo(Packet):
	pass


class S2C_GuildGVE_MonsterNtf(Packet):
	pass


class S2C_GuildGVE_OpenNtf(Packet):
	pass


class S2C_GuildGVE_AdditionNtf(Packet):
	pass


class C2S_GuildGVE_Sweep(Packet):
	pass


class S2C_GuildGVE_Sweep(Packet):
	pass


class S2C_FlushUserSignIn(Packet):
	pass


class C2S_SignIn_DailyAward(Packet):
	pass


class S2C_SignIn_DailyAward(Packet):
	pass


class C2S_SignIn_CumulateAward(Packet):
	pass


class S2C_SignIn_CumulateAward(Packet):
	pass


class C2S_Pet_UpLevel(Packet):
	pass


class S2C_Pet_UpLevel(Packet):
	pass


class C2S_Pet_UpQuality(Packet):
	pass


class S2C_Pet_UpQuality(Packet):
	pass


class C2S_Pet_UpQuality_OneKey(Packet):
	pass


class S2C_Pet_UpQuality_OneKey(Packet):
	pass


class C2S_Pet_Formation_Equip(Packet):
	pass


class S2C_Pet_Formation_Equip(Packet):
	pass


class C2S_Pet_Equipment_UpLevel(Packet):
	pass


class S2C_Pet_Equipment_UpLevel(Packet):
	pass


class C2S_Pet_Equipment_Equip(Packet):
	pass


class S2C_Pet_Equipment_Equip(Packet):
	pass


class C2S_Pet_Equipment_Lock(Packet):
	pass


class S2C_Pet_Equipment_Lock(Packet):
	pass


class C2S_Pet_Compose_Active(Packet):
	pass


class S2C_Pet_Compose_Active(Packet):
	pass


class C2S_Pet_Recruit_GetInfo(Packet):
	pass


class S2C_Pet_Recruit_GetInfo(Packet):
	pass


class C2S_Pet_Recruit_Roll(Packet):
	pass


class S2C_Pet_Recruit_Roll(Packet):
	pass


class C2S_Pet_Recruit_Select(Packet):
	pass


class S2C_Pet_Recruit_Select(Packet):
	pass


class C2S_Pet_Recruit_SetMultiple(Packet):
	pass


class S2C_Pet_Recruit_SetMultiple(Packet):
	pass


class C2S_Secret_GetInfo(Packet):
	pass


class S2C_Secret_GetInfo(Packet):
	pass


class C2S_Secret_ChallengeBegin(Packet):
	pass


class S2C_Secret_ChallengeBegin(Packet):
	pass


class S2C_Secret_ChallengeFinish(Packet):
	pass


class C2S_Secret_GetBossInfo(Packet):
	pass


class S2C_Secret_GetBossInfo(Packet):
	pass


class C2S_Secret_EnterBossRoom(Packet):
	pass


class S2C_Secret_EnterBossRoom(Packet):
	pass


class C2S_Secret_LeaveBossRoom(Packet):
	pass


class S2C_Secret_LeaveBossRoom(Packet):
	pass


class C2S_Secret_GetBossRankList(Packet):
	pass


class S2C_Secret_GetBossRankList(Packet):
	pass


class C2S_Secret_ClearBossCD(Packet):
	pass


class S2C_Secret_ClearBossCD(Packet):
	pass


class C2S_Secret_ChallengeBossBegin(Packet):
	pass


class S2C_Secret_ChallengeBossBegin(Packet):
	pass


class S2C_Secret_ChallengeBossFinish(Packet):
	pass


class C2S_Secret_ChallengeQuick(Packet):
	pass


class S2C_Secret_ChallengeQuick(Packet):
	pass


class S2C_Secret_BossRankAward(Packet):
	pass


class S2C_Secret_BossRankNotify(Packet):
	pass


class C2S_PeakArena_GetInfo(Packet):
	pass


class S2C_PeakArena_GetInfo(Packet):
	pass


class C2S_PeakArena_RefreshMatch(Packet):
	pass


class S2C_PeakArena_RefreshMatch(Packet):
	pass


class C2S_PeakArena_ChallengeBegin(Packet):
	pass


class S2C_PeakArena_ChallengeBegin(Packet):
	pass


class S2C_PeakArena_ChallengeFinish(Packet):
	pass


class C2S_PeakArena_GetDefendTeamDetail(Packet):
	pass


class S2C_PeakArena_GetDefendTeamDetail(Packet):
	pass


class C2S_PeakArena_SetTeam(Packet):
	pass


class S2C_PeakArena_SetTeam(Packet):
	pass


class C2S_PeakArena_GetBattleRecord(Packet):
	pass


class S2C_PeakArena_GetBattleRecord(Packet):
	pass


class S2C_PeakArena_NotifyAttacked(Packet):
	pass


class C2S_PeakArena_GetRank(Packet):
	pass


class S2C_PeakArena_GetRank(Packet):
	pass


class C2S_PeakArena_Sweep(Packet):
	pass


class S2C_PeakArena_Sweep(Packet):
	pass


class S2C_FlushCompetitions(Packet):
	pass


class C2S_Competition_ObtainQuestAward(Packet):
	pass


class S2C_Competition_ObtainQuestAward(Packet):
	pass


class C2S_Competition_ObtainScoreAward(Packet):
	pass


class S2C_Competition_ObtainScoreAward(Packet):
	pass


class C2S_TerritoryLord_GetInfo(Packet):
	pass


class S2C_TerritoryLord_GetInfo(Packet):
	pass


class C2S_TerritoryLord_CaptureChallengeBegin(Packet):
	pass


class S2C_TerritoryLord_CaptureChallengeBegin(Packet):
	pass


class S2C_TerritoryLord_CaptureChallengeFinish(Packet):
	pass


class C2S_TerritoryLord_EscapeChallengeBegin(Packet):
	pass


class S2C_TerritoryLord_EscapeChallengeBegin(Packet):
	pass


class S2C_TerritoryLord_EscapeChallengeFinish(Packet):
	pass


class C2S_TerritoryLord_FastEscape(Packet):
	pass


class S2C_TerritoryLord_FastEscape(Packet):
	pass


class C2S_TerritoryLord_SetConfrontState(Packet):
	pass


class S2C_TerritoryLord_SetConfrontState(Packet):
	pass


class C2S_TerritoryLord_LevyAward(Packet):
	pass


class S2C_TerritoryLord_LevyAward(Packet):
	pass


class C2S_TerritoryLord_GrantAward(Packet):
	pass


class S2C_TerritoryLord_GrantAward(Packet):
	pass


class C2S_TerritoryLord_Recommend(Packet):
	pass


class S2C_TerritoryLord_Recommend(Packet):
	pass


class C2S_TerritoryLord_Search(Packet):
	pass


class S2C_TerritoryLord_Search(Packet):
	pass


class C2S_TerritoryLord_ReleaseVassal(Packet):
	pass


class S2C_TerritoryLord_ReleaseVassal(Packet):
	pass


class C2S_TerritoryLord_FastSetConfrontState(Packet):
	pass


class S2C_TerritoryLord_FastSetConfrontState(Packet):
	pass


class C2S_TerritoryLord_RefreshRecommend(Packet):
	pass


class S2C_TerritoryLord_RefreshRecommend(Packet):
	pass


class S2C_TerritoryLord_Notify(Packet):
	pass


class C2S_Pack_Buy(Packet):
	pass


class S2C_Pack_Buy(Packet):
	pass


class C2S_FestivalActivity_GetInfo(Packet):
	pass


class S2C_FestivalActivity_GetInfo(Packet):
	pass


class C2S_FestivalActivity_StageChallenge(Packet):
	pass


class S2C_FestivalActivity_StageChallenge(Packet):
	pass


class C2S_FestivalActivity_StageEnd(Packet):
	pass


class S2C_FestivalActivity_StageEnd(Packet):
	pass


class C2S_FestivalActivity_QuestAward(Packet):
	pass


class S2C_FestivalActivity_QuestAward(Packet):
	pass


class S2C_FestivalActivity_NoticeInfo(Packet):
	pass


class C2S_Slg_Enter(Packet):
	pass


class S2C_Slg_Enter(Packet):
	pass


class C2S_Slg_UpgradeMainCity(Packet):
	pass


class S2C_Slg_UpgradeMainCity(Packet):
	pass


class C2S_Slg_StationMainCity(Packet):
	pass


class S2C_Slg_StationMainCity(Packet):
	pass


class C2S_Slg_UpgradeBarrack(Packet):
	pass


class S2C_Slg_UpgradeBarrack(Packet):
	pass


class C2S_Slg_UpgradeSupply(Packet):
	pass


class S2C_Slg_UpgradeSupply(Packet):
	pass


class C2S_Slg_ObtainSupplyReward(Packet):
	pass


class S2C_Slg_ObtainSupplyReward(Packet):
	pass


class C2S_Slg_UseSupplyToken(Packet):
	pass


class S2C_Slg_UseSupplyToken(Packet):
	pass


class S2C_Slg_NotifyActivity(Packet):
	pass


class C2S_Slg_MoveHome(Packet):
	pass


class S2C_Slg_MoveHome(Packet):
	pass


class C2S_Slg_GetMapShowData(Packet):
	pass


class S2C_Slg_GetMapShowData(Packet):
	pass


class C2S_Slg_GetMapSimpleShowData(Packet):
	pass


class S2C_Slg_GetMapSimpleShowData(Packet):
	pass


class S2C_Slg_FlushBattleResults(Packet):
	pass


class C2S_Slg_ObtainBattleReward(Packet):
	pass


class S2C_Slg_ObtainBattleReward(Packet):
	pass


class S2C_Slg_NotifyMoveUnit(Packet):
	pass


class C2S_Slg_Leave(Packet):
	pass


class S2C_Slg_Leave(Packet):
	pass


class S2C_Slg_NotifyMapShow(Packet):
	pass


class C2S_Slg_ObtainSupplyRewardsByAdv(Packet):
	pass


class S2C_Slg_ObtainSupplyRewardsByAdv(Packet):
	pass


class C2S_Slg_ObtainPreheatRewards(Packet):
	pass


class S2C_Slg_ObtainPreheatRewards(Packet):
	pass


class C2S_Slg_GetUserShowStatistics(Packet):
	pass


class S2C_Slg_GetUserShowStatistics(Packet):
	pass


class C2S_Slg_GetUserShowRankStatistic(Packet):
	pass


class S2C_Slg_GetUserShowRankStatistic(Packet):
	pass


class C2S_Slg_ObtainShowRewards(Packet):
	pass


class S2C_Slg_ObtainShowRewards(Packet):
	pass


class C2S_Slg_BossCreateTeam(Packet):
	pass


class S2C_Slg_BossCreateTeam(Packet):
	pass


class C2S_Slg_BossJoinTeam(Packet):
	pass


class S2C_Slg_BossJoinTeam(Packet):
	pass


class C2S_Slg_BossTeamKickOut(Packet):
	pass


class S2C_Slg_BossTeamKickOut(Packet):
	pass


class C2S_Slg_BossTransferLeader(Packet):
	pass


class S2C_Slg_BossTransferLeader(Packet):
	pass


class C2S_Slg_BossLeave(Packet):
	pass


class S2C_Slg_BossLeave(Packet):
	pass


class C2S_Slg_BossTeamList(Packet):
	pass


class S2C_Slg_BossTeamList(Packet):
	pass


class C2S_Slg_BossTeamInfo(Packet):
	pass


class S2C_Slg_BossTeamInfo(Packet):
	pass


class S2C_Slg_BossUserStateNotify(Packet):
	pass


class S2C_Slg_BossTeamJoinNotify(Packet):
	pass


class S2C_Slg_BossBattleStartNotify(Packet):
	pass


class S2C_Slg_BossBattleFinishNotify(Packet):
	pass


class C2S_Slg_BossDismissTeam(Packet):
	pass


class S2C_Slg_BossDismissTeam(Packet):
	pass


class C2S_Slg_BossMonsterTeam(Packet):
	pass


class S2C_Slg_BossMonsterTeam(Packet):
	pass


class C2S_Slg_BossQuickJoinTeam(Packet):
	pass


class S2C_Slg_BossQuickJoinTeam(Packet):
	pass


class C2S_Slg_GetReport(Packet):
	pass


class S2C_Slg_GetReport(Packet):
	pass


class C2S_Slg_GetRank(Packet):
	pass


class S2C_Slg_GetRank(Packet):
	pass


class C2S_Slg_SimulateBattle(Packet):
	pass


class S2C_Slg_SimulateBattle(Packet):
	pass


class C2S_Slg_CityMarch(Packet):
	pass


class S2C_Slg_CityMarch(Packet):
	pass


class C2S_Slg_CityCancelMove(Packet):
	pass


class S2C_Slg_CityCancelMove(Packet):
	pass


class C2S_Slg_GetCityGather(Packet):
	pass


class S2C_Slg_GetCityGather(Packet):
	pass


class C2S_Slg_GetCityDefInfo(Packet):
	pass


class S2C_Slg_GetCityDefInfo(Packet):
	pass


class S2C_Slg_CityNtf(Packet):
	pass


class S2C_Slg_CityBattleEnd(Packet):
	pass


class C2S_Slg_CityDeclare(Packet):
	pass


class S2C_Slg_CityDeclare(Packet):
	pass


class S2C_Slg_CityDeclareNtf(Packet):
	pass


class S2C_Slg_CityBeDeclaredNtf(Packet):
	pass


class S2C_Slg_CityMarchNtf(Packet):
	pass


class C2S_Slg_BuildCity(Packet):
	pass


class S2C_Slg_BuildCity(Packet):
	pass


class C2S_Slg_GetCityBuildInfo(Packet):
	pass


class S2C_Slg_GetCityBuildInfo(Packet):
	pass


class S2C_Slg_CityBattleGuildSummaryNtf(Packet):
	pass


class C2S_Slg_GetInfoOnCityBattleEnd(Packet):
	pass


class S2C_Slg_GetInfoOnCityBattleEnd(Packet):
	pass


class C2S_Slg_SetCityDeclaration(Packet):
	pass


class S2C_Slg_SetCityDeclaration(Packet):
	pass


class C2S_Slg_PVEMarch(Packet):
	pass


class S2C_Slg_PVEMarch(Packet):
	pass


class C2S_Slg_MainQuestAward(Packet):
	pass


class S2C_Slg_MainQuestAward(Packet):
	pass


class C2S_Slg_CityQuestAward(Packet):
	pass


class S2C_Slg_CityQuestAward(Packet):
	pass


class C2S_Slg_GetBattlePassInfo(Packet):
	pass


class S2C_Slg_GetBattlePassInfo(Packet):
	pass


class C2S_Slg_BattlePassAwardQuest(Packet):
	pass


class S2C_Slg_BattlePassAwardQuest(Packet):
	pass


class S2C_Slg_BattlePassBuyNtf(Packet):
	pass


class C2S_Slg_BattlePassBuyLv(Packet):
	pass


class S2C_Slg_BattlePassBuyLv(Packet):
	pass


class C2S_Slg_BattlePassAwardLv(Packet):
	pass


class S2C_Slg_BattlePassAwardLv(Packet):
	pass


class C2S_Slg_GetMonsterInfo(Packet):
	pass


class S2C_Slg_GetMonsterInfo(Packet):
	pass


class C2S_Slg_PVEWithdraw(Packet):
	pass


class S2C_Slg_PVEWithdraw(Packet):
	pass


class S2C_Slg_SyncUserTeam(Packet):
	pass


class S2C_Slg_PVEBattleReport(Packet):
	pass


class C2S_Slg_GetUserDetail(Packet):
	pass


class S2C_Slg_GetUserDetail(Packet):
	pass


class S2C_Slg_SyncMainQuest(Packet):
	pass


class S2C_Slg_PVEBattleResult(Packet):
	pass


class S2C_Slg_NotifyCheckpointQuest(Packet):
	pass


class S2C_Slg_NotifyCheckpointQuestAward(Packet):
	pass


class S2C_Slg_SyncCityQuestProgress(Packet):
	pass


class C2S_Slg_EditUserTeam(Packet):
	pass


class S2C_Slg_EditUserTeam(Packet):
	pass


class S2C_Slg_SyncUserScore(Packet):
	pass


class C2S_Slg_ObtainQuestReward(Packet):
	pass


class S2C_Slg_ObtainQuestReward(Packet):
	pass


class C2S_Slg_OnekeyObtainRewards(Packet):
	pass


class S2C_Slg_OnekeyObtainRewards(Packet):
	pass


class C2S_Guild_RedPacket_GetInfo(Packet):
	pass


class S2C_Guild_RedPacket_GetInfo(Packet):
	pass


class C2S_Guild_RedPacket_Send(Packet):
	pass


class S2C_Guild_RedPacket_Send(Packet):
	pass


class C2S_Guild_RedPacket_Pick(Packet):
	pass


class S2C_Guild_RedPacket_Pick(Packet):
	pass


class C2S_Guild_RedPacket_Open(Packet):
	pass


class S2C_Guild_RedPacket_Open(Packet):
	pass


class C2S_WishPool_GetInfo(Packet):
	pass


class S2C_WishPool_GetInfo(Packet):
	pass


class C2S_WishPool_DailyAward(Packet):
	pass


class S2C_WishPool_DailyAward(Packet):
	pass


class C2S_WishPool_Draw(Packet):
	pass


class S2C_WishPool_Draw(Packet):
	pass


class C2S_WishPool_Exchange(Packet):
	pass


class S2C_WishPool_Exchange(Packet):
	pass


class C2S_WishPool_GetResource(Packet):
	pass


class S2C_WishPool_GetResource(Packet):
	pass


class S2C_WishPool_Sync(Packet):
	pass


class C2S_Goblin_WearDress(Packet):
	pass


class S2C_Goblin_WearDress(Packet):
	pass


class C2S_Gacha_GetInfo(Packet):
	pass


class S2C_Gacha_GetInfo(Packet):
	pass


class C2S_Gacha_ChoseAward(Packet):
	pass


class S2C_Gacha_ChoseAward(Packet):
	pass


class C2S_Gacha_QuestAward(Packet):
	pass


class S2C_Gacha_QuestAward(Packet):
	pass


class C2S_Gacha_Draw(Packet):
	pass


class S2C_Gacha_Draw(Packet):
	pass


class C2S_Gacha_Reset(Packet):
	pass


class S2C_Gacha_Reset(Packet):
	pass


class C2S_Gacha_AccumulatedAward(Packet):
	pass


class S2C_Gacha_AccumulatedAward(Packet):
	pass


class C2S_CirculateAct_GetInfo(Packet):
	pass


class S2C_CirculateAct_GetInfo(Packet):
	pass


class C2S_CirculateAct_QuestAward(Packet):
	pass


class S2C_CirculateAct_QuestAward(Packet):
	pass


class C2S_Alchemy_GetInfo(Packet):
	pass


class S2C_Alchemy_GetInfo(Packet):
	pass


class C2S_Alchemy_GuildChests(Packet):
	pass


class S2C_Alchemy_GuildChests(Packet):
	pass


class C2S_Alchemy_ObtainChestAward(Packet):
	pass


class S2C_Alchemy_ObtainChestAward(Packet):
	pass


class C2S_Alchemy_PotionCompose(Packet):
	pass


class S2C_Alchemy_PotionCompose(Packet):
	pass


class C2S_Alchemy_Build(Packet):
	pass


class S2C_Alchemy_Build(Packet):
	pass


class S2C_Alchemy_AwardLogNotify(Packet):
	pass


class C2S_Alchemy_RequestLogs(Packet):
	pass


class S2C_Alchemy_RequestLogs(Packet):
	pass


class C2S_Alchemy_SendRequest(Packet):
	pass


class S2C_Alchemy_SendRequest(Packet):
	pass


class C2S_Alchemy_SupportRequest(Packet):
	pass


class S2C_Alchemy_SupportRequest(Packet):
	pass


class C2S_Alchemy_ObtainRequestAward(Packet):
	pass


class S2C_Alchemy_ObtainRequestAward(Packet):
	pass


class C2S_Alchemy_RequestList(Packet):
	pass


class S2C_Alchemy_RequestList(Packet):
	pass


class S2C_Alchemy_SupportNotify(Packet):
	pass


class S2C_Alchemy_AppendGuildChestNotify(Packet):
	pass


class C2S_Alchemy_ObtainGuildPointAward(Packet):
	pass


class S2C_Alchemy_ObtainGuildPointAward(Packet):
	pass


class C2S_Alchemy_ObtainQuestAward(Packet):
	pass


class S2C_Alchemy_ObtainQuestAward(Packet):
	pass


class S2C_Alchemy_SendRequestNotify(Packet):
	pass


class C2S_Alchemy_GetSimpleInfo(Packet):
	pass


class S2C_Alchemy_GetSimpleInfo(Packet):
	pass


class S2C_Advertisement_NotifyUpdate(Packet):
	pass


class S2C_Advertisement_NotifyDelete(Packet):
	pass


class C2S_ScrollAnnounce_GetInfo(Packet):
	pass


class S2C_ScrollAnnounce_GetInfo(Packet):
	pass


class S2C_ScrollAnnounce_Update(Packet):
	pass


class C2S_SelectGift_Buy(Packet):
	pass


class S2C_SelectGift_Buy(Packet):
	pass


class S2C_SelectGift_NotifyTrigger(Packet):
	pass


class C2S_PersonalComp_GetInfo(Packet):
	pass


class S2C_PersonalComp_GetInfo(Packet):
	pass


class C2S_PersonalComp_AwardQuest(Packet):
	pass


class S2C_PersonalComp_AwardQuest(Packet):
	pass


class C2S_PersonalComp_AwardScore(Packet):
	pass


class S2C_PersonalComp_AwardScore(Packet):
	pass


class C2S_GuildGvg_GetInfo(Packet):
	pass


class S2C_GuildGvg_GetInfo(Packet):
	pass


class C2S_GuildGvg_GuildMatchDetail(Packet):
	pass


class S2C_GuildGvg_GuildMatchDetail(Packet):
	pass


class C2S_GuildGvg_ChallengeBegin(Packet):
	pass


class S2C_GuildGvg_ChallengeBegin(Packet):
	pass


class S2C_GuildGvg_ChallengeFinish(Packet):
	pass


class C2S_GuildGvg_Weaken(Packet):
	pass


class S2C_GuildGvg_Weaken(Packet):
	pass


class C2S_GuildGvg_GuildContributeRank(Packet):
	pass


class S2C_GuildGvg_GuildContributeRank(Packet):
	pass


class C2S_GuildGvg_GetUserDetail(Packet):
	pass


class S2C_GuildGvg_GetUserDetail(Packet):
	pass


class C2S_GuildGvg_GetBattleRecords(Packet):
	pass


class S2C_GuildGvg_GetBattleRecords(Packet):
	pass


class S2C_GuildGvg_BattleLogNotify(Packet):
	pass


class C2S_GuildGvg_BattleLogLike(Packet):
	pass


class S2C_GuildGvg_BattleLogLike(Packet):
	pass


class C2S_GuildGvg_GuildRank(Packet):
	pass


class S2C_GuildGvg_GuildRank(Packet):
	pass


class C2S_GuildGvg_GetUserBase(Packet):
	pass


class S2C_GuildGvg_GetUserBase(Packet):
	pass


class C2S_GuildGvg_BattleResult(Packet):
	pass


class S2C_GuildGvg_BattleResult(Packet):
	pass


class S2C_GuildGvg_BattleDefendNotify(Packet):
	pass


class C2S_GuildGvg_SetDefendFormation(Packet):
	pass


class S2C_GuildGvg_SetDefendFormation(Packet):
	pass


class C2S_PiggyBank_ObtainAward(Packet):
	pass


class S2C_PiggyBank_ObtainAward(Packet):
	pass


class S2C_PiggyBank_NotifyRechargeSuccess(Packet):
	pass


class  quiet(Packet):
	pass


class  quiet(Packet):
	pass


class BattleReport(Packet):
	pass


class BattleResult(Packet):
	pass

class C2S_TeamBoss_CreateTeam(Packet):
	pass