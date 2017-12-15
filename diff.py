---------------------------
设备管理
{
    1. 按房间查询设备列表接口(00101001)
    {
        content:
        {
            code: 0
            method: dm_get_devices_by_room
            msg: success
            req_id: no_need
            result:
            {
                family_id: 2031 - -----------------------------------------------------------------------------actuality only
                [
                    {
                        attribute: no_need
                        created_at: no_need
                        default_device_name: no_need
                        device_category_id: 5
                        device_id: no_need
                        device_name: no_need
                        device_uuid: no_need
                        family_id: 2031
                        room_id: 3
                        updated_at: no_need
                    }
                ]
                more: 0
                user_id: 2030
            }
            timestamp: no_need
        }
        encry: no_need
        uuid: no_need
    }

    2. 添加子设备接口(00101005)
    {
        content:
        {
            code: 0
            method: dm_add_device
            msg: success
            msg_code: 0 - -----------------------------------------------------------------------------------actuality only
            msg_tag: no_need - ------------------------------------------------------------------------------expected only
            req_id: no_need
            result:
            {
                attribute:
                {
                    b: no_need
                    connectivity: online
                    g: no_need
                    hue: no_need
                    level: no_need
                    mode: on
                    r: no_need
                    saturation: no_need
                    temperature: no_need
                }
                bussiness_user_id: 0
                create_at: no_need
                device_category_id: 5
                device_id: no_need
                device_name: no_need
                device_uuid: no_need
                family_id: 2031
                room_id: 1
                room_name: å®¢å
                update_at: no_need
                user_id: 2030
            }
            timestamp: no_need
        }
        encry: no_need
        uuid: no_need
    }

    3. 取消添加子设备接口(00101008)
    {
      content :
      {
        code : 0
        method : dm_add_device_abort
        msg : success
        msg_code : 0------------------------------------------------------------------------------------actuality only
        msg_tag : no_need-------------------------------------------------------------------------------expected only
        req_id : no_need
        result :
        {
          user_id : 2030--------------------------------------------------------------------------------expected only
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    4. 删除子设备接口(00101002)
    {
      content :
      {
        code : 0
        method : dm_del_device
        msg : success
        msg_tag : no_need-------------------------------------------------------------------------------expected only
        req_id : no_need
        result :
        {
          device_id : no_need
          device_uuid : 050000000200000142810b11004b1200------------------------------------------------actuality only
          family_id : 2031
          status : removed------------------------------------------------------------------------------actuality only
          user_id : 2030
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    5. 获取设备信息接口(00101009)

    6. 查询某个品类的设备列表接口(00101011)
    {
        "content": {
            "code": 0,
            "method": "dm_get_devices_by_family",
            "msg": "success",
            "req_id": 123,
            "result": {
                "family_id" : 2031------------------------------------------------------------------------------expected only
                "user_id" : 2030--------------------------------------------------------------------------------expected only
                "list": [
                    {
                        "attribute": {
                            "connectivity": "online",
                            "deviceCategory": "airconditioner.new",
                            "deviceModel": "KFR-50LW/10CBB23AU1",
                            "deviceSubCategory": 1,
                            "manufactureId": "haier",
                            "mode": "auto",
                            "speed": "high",
                            "switchStatus": "on",
                            "temperature": 17,
                            "wind_left_right": "off",
                            "wind_up_down": "off"
                        },
                        "created_at": 1513224149,
                        "default_device_name": "柜式空调",
                        "device_category_id": 1,
                        "device_id": 33685849,
                        "device_name": "柜式空调",
                        "device_uuid": "000e83c6c10000000000000002020159",
                        "family_id": 2031,
                        "room_id": 2,
                        "updated_at": 1513224149,
                        "user_id" : 2030------------------------------------------------------------------------actuality only
                    }
                ],
                "more": 0
            },
            "timestamp": 1513224189
        },
        "encry": "false",
        "uuid": "00fbfca7bf0000000000000001021717"
    }

    7. 按家庭查询设备列表接口(00101012)

    8. 修改设备名称接口(00101013)
    {
      content :
      {
        code : 0
        method : dm_update_device
        msg : success
        msg_tag : no_need
        req_id : 123
        result :
        {
          attribute : no_need
          bussiness_user_id : no_need
          create_at : no_need---------------------------------------------------------------------------expected only
          device_category_id : 1
          device_id : no_need
          device_name : 柜式空调_new
          device_uuid : 000e83c6c10000000000000002020159
          family_id : 2031
          room_id : 2
          update_at : no_need---------------------------------------------------------------------------expected only
          user_id : 2030
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    9. 转移子设备到新房间接口(00101015)
    {
      content :
      {
        code : 0
        method : dm_move_devices
        msg : success
        msg_tag : no_need-------------------------------------------------------------------------------expected only
        req_id : no_need
        result :
        {
          family_id : 2031------------------------------------------------------------------------------actuality only
          [
            {
              attribute : no_need-----------------------------------------------------------------------expected only
              bussiness_user_id : no_need---------------------------------------------------------------expected only
              create_at : no_need-----------------------------------------------------------------------expected only
              device_category_id : no_need--------------------------------------------------------------expected only
              device_id : no_need
              device_name : no_need
              device_uuid : no_need
              room_id : 1
              family_id : no_need-----------------------------------------------------------------------expected only
              update_at : no_need-----------------------------------------------------------------------expected only
              user_id : no_need-------------------------------------------------------------------------expected only
            }
          ]
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    10. 获取家庭已入网设备品类列表(00101019)

    11. 获取设备类型列表(00101017)
    {
      content :
      {
        code : 0
        method : dm_get_dev_type_list
        msg : success
        msg_tag :
        req_id : 123
        result :
        {
          family_id : 2031------------------------------------------------------------------------------actuality only
          user_id : 2030--------------------------------------------------------------------------------actuality only
          [
            {
              created_at : no_need
              id : 1
              name : 空调
              order : 1
              updated_at : no_need
            }
            {
              created_at : no_need
              id : 2
              name : 窗帘
              order : 2
              updated_at : no_need
            }
          ]
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    12. 获取产品列表 (00101021)

    13. 获取品类对应属性列表 (00101024)

    14. 获取产品ID对应属性列表(00101026)

    15. 设备控制的异步应答(00101023)
    {
      content :
      {
        method : mdp_msg
        params :
        {
          content :
          {
            method : dr_report_dev_status
            result :
            {
              attribute :
              {
                b : no_need
                connectivity : no_need
                g : no_need
                hue : no_need
                level : no_need
                mode : on-------------------------------------------------------------------------------actuality only
                r : no_need
                saturation : no_need
                switch_status : no_need-----------------------------------------------------------------expected only
                temperature : no_need
              }
              device_category_id : no_need
              device_id : no_need
              device_uuid : no_need
              family_id : no_need
              status_modified_at : no_need
              timestamp : no_need
              updated_at : no_need
            }
          }
          msg_type : no_need
          target_id : no_need
        }
        req_id : no_need
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }
}
---------------------------
房间主页管理
{
    1. 快捷方式排序(00104001)
    {
      content :
      {
        code : 0
        method : dm_sort_shortcut
        msg : success
        msg_tag : no_need
        req_id : no_need
        result :
        {
          family_id : 2031
          list : [{u'shortcut_id': 1, u'order': u'2'}, {u'shortcut_id': 2, u'order': u'1'}]-------------actuality only
          room_id : 1-----------------------------------------------------------------------------------actuality only
          user_id : 2030
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    2. 获取当前快捷方式列表(00104002)
    {
        "content": {
            "code": 0,
            "method": "dm_get_shortcut_list",
            "msg": "success",
            "msg_tag": "xxxx",
            "req_id": 178237278,
            "result": {
                "family_id": 2031,
                "list": [
                    {
                        "content": [
                            {
                                "device_category_id": 5,
                                "device_name": "佛照多孔射灯",
                                "device_uuid": "050000000200000142810b11004b1200"
                            }
                        ],
                        "device_category_id": -2,
                        "device_uuid": "1",---------------------------------------------------------actuality only
                        "level": 75,
                        "mode": "on",
                        "name": "全屋灯",
                        "order": 1,
                        "room_id": 1,
                        "shortcut_id": 2
                    },
                    {
                        "content": [
                            {
                                "device_category_id": 5,
                                "device_name": "佛照多孔射灯",
                                "device_uuid": "050000000200000142810b11004b1200"
                            }
                        ],
                        "device_category_id": -1,
                        "device_uuid": "0",---------------------------------------------------------actuality only
                        "mode": "on",
                        "name": "总开关",
                        "order": 2,
                        "room_id": 1,
                        "shortcut_id": 1
                    },
                    {
                        "content": [
                            {
                                "attribute": {
                                },
                                "device_uuid": "050000000200000142810b11004b1200"
                            }
                        ],
                        "device_category_id": 1 VS -3,---------------------------------------------------------mismatch
                        "name": "空调-风速",
                        "order": 3,
                        "room_id": 1,
                        "shortcut_id": 13
                    }
                ],
                "user_id": 2030
            },
            "timestamp": 1513254408
        },
        "encry": "false",
        "uuid": "00fbfca7bf0000000000000001021717"
    }

    3. 添加快捷方式(00104003)
    {
      content :
      {
        code : 0
        method : dm_add_shortcut
        msg : success
        msg_tag : no_need
        req_id : no_need
        result :
        {
            "content": [
                {
                    attribute : ------------------------------------------------------------------------------actuality only
                    {
                        connectivity : online-------------------------------------------------------------------actuality only
                        speed : high----------------------------------------------------------------------------actuality only
                        switchStatus : on-----------------------------------------------------------------------actuality only
                    }
                    device_id : no_need-----------------------------------------------------------------------expected only
                    name : 空调-风速---------------------------------------------------------------------------expected only
                    device_uuid : 000e83c6c10000000000000002020159
                }
            ]
            device_category_id : 1
            family_id : 2031
            mode : on
            name : 空调-风速
            order : 3
            room_id : 1
            shortcut_id : 13
            user_id : 2030
        }
        timestamp : no_need
      }
      encry : no_need
      uuid : no_need
    }

    4. 删除快捷方式(00104004)

    5. 获取设备属性过滤条件列表(00104005)
    {
        "content": {
            "code": 0,
            "method": "dm_get_shortcut_filter",
            "msg": "success",
            "msg_tag": "success",
            "req_id": 178237278,
            "result": {
                "family_id" : 2031------------------------------------------------------------------------------expected only
                "user_id" : 2030--------------------------------------------------------------------------------expected only
                "list": [
                    {
                        "device_category_id": 1,
                        "device_name": "空调",
                        "filter": [
                            {
                                "decription": "温度",
                                "id": 1,------------------------------------------------------------------------actuality only
                                'property_id': 1,---------------------------------------------------------------expected only
                                "name": "temperature"
                            },
                            {
                                "decription": "风速",
                                "id": 2,
                                "name": "speed"
                            }
                        ]
                    }
                ]
            },
            "timestamp": 1513245985
        },
        "encry": "false",
        "uuid": "00fbfca7bf0000000000000001021717"
    }

    6. 修改总开关绑定设备(00104006)

    7. 开启/关闭总开关(00104007)--send
    {
        "content":{
            "timestamp":1498111457196,
            "params":{
                "family_id":2031,
                "room_id":1,
                "mode":"on",
                "data":[
                    {
                        "timestamp":123456789,
                        "params":{
                            "attribute":{
                                "mode":"on",--------------------------------------------------------------------actuality only
                                "switch": "on"------------------------------------------------------------------expected only
                            },
                            "user_id": 2003,--------------------------------------------------------------------expected only
                            "cmd":"setOnoff",-------------------------------------------------------------------actuality only
                            "device_uuid":"050000000200000142810b11004b1200"
                        },
                        "method": "dm_set" VS "dm_set_zigbee_bulb",---------------------------------------------mismatch
                        "req_id":178237278,
                        "nodeid":"bulb.main.switch"
                    }
                ],
                "user_id":2030
            },
            "method":"dm_set_total_control",
            "req_id":178237278
        },
        "encry":"false",
        "uuid":"111"
    }

    8. 开启/关闭全屋灯(00104008)
}
---------------------------
空调控制
{

}
---------------------------
