package com.teamventure.infrastructure.persistence.po;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

@TableName("users")
public class UserPO {
    @TableId
    private String user_id;
    private String wechat_openid;
    private String nickname;
    private String role;
    private String status;

    public String getUserId() { return user_id; }
    public void setUserId(String v) { this.user_id = v; }
    public String getWechatOpenid() { return wechat_openid; }
    public void setWechatOpenid(String v) { this.wechat_openid = v; }
    public String getNickname() { return nickname; }
    public void setNickname(String v) { this.nickname = v; }
    public String getRole() { return role; }
    public void setRole(String v) { this.role = v; }
    public String getStatus() { return status; }
    public void setStatus(String v) { this.status = v; }
}

