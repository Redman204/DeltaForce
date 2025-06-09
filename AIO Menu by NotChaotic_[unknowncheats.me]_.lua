


------------------------------------------------------------------------------------------------------------------------------------------------------
function getMP()
	if stats.get_int("MPPLY_LAST_MP_CHAR") == 1 then
		return "MP1_"
	else
		return "MP0_"
	end
end

function getSP()
	if ENTITY.GET_ENTITY_MODEL(PLAYER.PLAYER_PED_ID()) == joaat("Player_Zero") then
		return "SP0_"
	elseif ENTITY.GET_ENTITY_MODEL(PLAYER.PLAYER_PED_ID()) == joaat("Player_One") then
		return "SP1_"
	elseif ENTITY.GET_ENTITY_MODEL(PLAYER.PLAYER_PED_ID()) == joaat("Player_Two") then
		return "SP2_"
	else
		return "SP0_"
	end
end


format_Number = function(value)
	return (tostring(value)):reverse():gsub("%d%d%d", "%1,"):reverse():gsub("^,", "")
end


format_Decimal = function(value, decimal_place)
	if decimal_place == nil then
		decimal_place = 0
	end
	return string.format("%." .. (decimal_place) .. "f", value)
end


is_int = function(value)
	return (type(value) == "number") and (math.floor(value) == value)
end
------------------------------------------------------------------------------------------------------------------------------------------------------





menu = gui.get_tab("All-In-One Menu")



------------------------------------------------------------------------------------------------------------------------------------------------------
Self_Options = menu:add_tab(" - Self")
Self_Options:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar(" - Self") then
            if ImGui.BeginTabItem("Player Stats") then
                Online_Player_Stamina_Stat = ImGui.Button("Max Stamina Ability")
                if Online_Player_Stamina_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_STAM", 100)
                end

                Online_Player_Shooting_Stat = ImGui.Button("Max Shooting Ability")
                if Online_Player_Shooting_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_SHO", 100)
                end

                Online_Player_Strength_Stat = ImGui.Button("Max Strength Ability")
                if Online_Player_Strength_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_STRN", 100)
                end

                Online_Player_Stealth_Stat = ImGui.Button("Max Stealth Ability")
                if Online_Player_Stealth_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_STL", 100)
                end

                Online_Player_Strength_Stat = ImGui.Button("Max Strength Ability")
                if Online_Player_Strength_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_FLY", 100)
                end

                Online_Player_Driving_Stat = ImGui.Button("Max Driving Ability")
                if Online_Player_Driving_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_DRIV", 100)
                end

                Online_Player_Lung_Stat = ImGui.Button("Max Lung Capacity")
                if Online_Player_Lung_Stat then
                    stats.set_int(getMP() .. "SCRIPT_INCREASE_LUNG", 100)
                end
                ImGui.EndTabItem()
            end
            if ImGui.BeginTabItem("Inventory") then

                Online_Player_Refill_Snacks = ImGui.Button("Refill Snacks")
                if Online_Player_Refill_Snacks then
                    stats.set_int(getMP() .. "NO_BOUGHT_YUM_SNACKS", 30)
                    stats.set_int(getMP() .. "NO_BOUGHT_HEALTH_SNACKS", 15)
                    stats.set_int(getMP() .. "NO_BOUGHT_EPIC_SNACKS", 5)
                    stats.set_int(getMP() .. "NUMBER_OF_CHAMP_BOUGHT", 5)
                    stats.set_int(getMP() .. "NUMBER_OF_ORANGE_BOUGHT", 11)
                    stats.set_int(getMP() .. "NUMBER_OF_BOURGE_BOUGHT", 10)
                    stats.set_int(getMP() .. "NUMBER_OF_SPRUNK_BOUGHT", 10)
                end

                Online_Player_Refill_Cigarettes = ImGui.Button("Refill Cigarettes")
                if Online_Player_Refill_Cigarettes then
                    stats.set_int(getMP() .. "CIGARETTES_BOUGHT", 20)
                end

                Online_Player_Refill_Armor = ImGui.Button("Refill Armor")
                if Online_Player_Refill_Armor then
                    stats.set_int(MPX() .. "MP_CHAR_ARMOUR_1_COUNT", 10)
                    stats.set_int(getMP() .. "MP_CHAR_ARMOUR_2_COUNT", 10)
                    stats.set_int(getMP() .. "MP_CHAR_ARMOUR_3_COUNT", 10)
                    stats.set_int(getMP() .. "MP_CHAR_ARMOUR_4_COUNT", 10)
                    stats.set_int(getMP() .. "MP_CHAR_ARMOUR_5_COUNT", 10)
                end

                Online_Player_Refill_Rebreather = ImGui.Button("Refill Rebreather")
                if Online_Player_Refill_Rebreather then
                    stats.set_int(getMP() .. "BREATHING_APPAR_BOUGHT", 20)
                end
                ImGui.EndTabItem()
            end
        end
    else
        SinglePlayer_Stats = ImGui.Button("Max Character Skills")
        if SinglePlayer_Stats then
            stats.set_int(getSP() .. "SPECIAL_ABILITY_UNLOCKED", 100)
            stats.set_float(getSP() .. "DIST_RUNNING", 175 * 100)
            stats.set_int(getSP() .. "TIME_UNDERWATER", 30 * 60 * 1000 * 100)
            stats.set_int(getSP() .. "UNARMED_HITS", 20 * 100)
            stats.set_int(getSP() .. "NUMBER_NEAR_MISS", 50 * 100)
            stats.set_int(getSP() .. "PLANE_LANDINGS", 10 * 100)
            stats.set_int(getSP() .. "KILLS_STEALTH", 2 * 100)
            stats.set_int(getSP() .. "HITS_MISSION", 40 * 100)
            stats.set_int(getSP() .. "HITS_PEDS_VEHICLES", 80 * 100)
        end
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------




------------------------------------------------------------------------------------------------------------------------------------------------------
Business_Manager = menu:add_tab(" - Business Manager")
Business_Manager:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar(" - Business Manager") then



            if ImGui.BeginTabItem("Disruption Logistics") then
                ImGui.SeparatorText("Master Control Terminal")
                Master_Control_Terminal = ImGui.Button("Access Business Management Portal")
                if Master_Control_Terminal then
                    SCRIPT.REQUEST_SCRIPT("apparcadebusinesshub")
                    SYSTEM.START_NEW_SCRIPT("apparcadebusinesshub", 8344)
                end



                if stats.get_int(getMP() .. "FACTORYSETUP5") == 0 then
                    DI_Setup = ImGui.Button("Setup Bunker Equipment")
                    if DI_Setup then
                        stats.set_int(getMP() .. "FACTORYSETUP5", 1)
                    end
                else
                    local Disruption_Logistics_Globals_Tunables = {
                        Manufacture = {
                            Capacity = function() return tunables.get_int("GR_MANU_CAPACITY") end,
                            Product = {
                                Base_Value = function() return tunables.get_int("GR_MANU_PRODUCT_VALUE") end,
                                Equipment_Addon_Value = function() return tunables.get_int("GR_MANU_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                                Staff_Addon_Value = function() return tunables.get_int("GR_MANU_PRODUCT_VALUE_STAFF_UPGRADE") end,
                                Foreign_Bonus = function() return tunables.get_float("GR_SELL_PRODUCT_FAR_MODIFIER") end
                            },
                            Weapon_Stock = function() return stats.get_int(getMP() .. "PRODTOTALFORFACTORY5") end
                        },
                        Research = {
                            Capacity = function() return tunables.get_int("GR_RESEARCH_CAPACITY") end,
                            Research_Percentage = function() return stats.get_int(getMP() .. "RESEARCHTOTALFORFACTORY5") end,
                            Current_Item = function() return stats.get_int(getMP() .. "GUNR_RESEARCH_ITEM") end
                        },
                        Supplies = {
                            Stock = function() return stats.get_int(getMP() .. "MATTOTALFORFACTORY5") end
                        },
                        Business = {
                            Status = function() return stats.get_int(getMP() .. "BKR_FACTORY_PROD_STOPPED") end,
                            Upgrades = {
                                Equipment = function() return stats.get_int(getMP() .. "BUNKER_EQUIPMENT") end,
                                Staff = function() return stats.get_int(getMP() .. "BUNKER_STAFF") end,
                                Security = function() return stats.get_int(getMP() .. "BUNKER_SECURITY") end
                            }
                        }
                    }

                    ImGui.Separator()
                    ImGui.SeparatorText("SUPPLIES")
                    ImGui.Text("    Current Supply Level: " .. Disruption_Logistics_Globals_Tunables.Supplies.Stock())



                    ImGui.Separator()
                    ImGui.SeparatorText("MANUFACTRURE")
                    if Disruption_Logistics_Globals_Tunables.Business.Upgrades.Equipment() == 1 and Disruption_Logistics_Globals_Tunables.Business.Upgrades.Staff() == 1 then
                        DL_Price_Per_Unit = Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value() + Disruption_Logistics_Globals_Tunables.Manufacture.Product.Staff_Addon_Value() + Disruption_Logistics_Globals_Tunables.Manufacture.Product.Equipment_Addon_Value()
                        
                        ImGui.Text("    Price Per Unit: $" .. format_Number(DL_Price_Per_Unit))
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Price Breakdown:\n - Base Value: $" .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value()) .. "\n - Equipment Upgrade Benefit: $" .. Disruption_Logistics_Globals_Tunables.Manufacture.Product.Equipment_Addon_Value() .. "\n - Staff Upgrade Benefit: $" .. Disruption_Logistics_Globals_Tunables.Manufacture.Product.Staff_Addon_Value())
                        end
                    elseif Disruption_Logistics_Globals_Tunables.Business.Upgrades.Equipment() == 1 then
                        DL_Price_Per_Unit = Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value() + Disruption_Logistics_Globals_Tunables.Manufacture.Product.Equipment_Addon_Value()
                        
                        ImGui.Text("    Price Per Unit: $" .. format_Number(DL_Price_Per_Unit))
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Price Breakdown:\n - Base Value: $" .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value()) .. "\n - Equipment Upgrade Benefit: $" .. Disruption_Logistics_Globals_Tunables.Manufacture.Product.Equipment_Addon_Value() .. "\n - Staff Upgrade Benefit: $0")
                        end
                    elseif Disruption_Logistics_Globals_Tunables.Business.Upgrades.Staff() == 1 then
                        DL_Price_Per_Unit = Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value() + Disruption_Logistics_Globals_Tunables.Manufacture.Product.Staff_Addon_Value()
                        
                        ImGui.Text("    Price Per Unit: $" .. format_Number(DL_Price_Per_Unit))
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Price Breakdown:\n - Base Value: $" .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value()) .. "\n - Equipment Upgrade Benefit: $0" .. "\n - Staff Upgrade Benefit: $" .. Disruption_Logistics_Globals_Tunables.Manufacture.Product.Staff_Addon_Value())
                        end
                    else
                        DL_Price_Per_Unit = Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value()
                        
                        ImGui.Text("    Price Per Unit: $" .. format_Number(DL_Price_Per_Unit))
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Price Breakdown:\n - Base Value: $" .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Product.Base_Value()) .. "\n - Equipment Upgrade Benefit: $0\n - Staff Upgrade Benefit: $0")
                        end
                    end

                    ImGui.Text("    Stock Level: " .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Weapon_Stock()) .. " / " .. format_Number(Disruption_Logistics_Globals_Tunables.Manufacture.Capacity()))
                    ImGui.Text("    Stock Price: $" .. format_Number(DL_Price_Per_Unit * Disruption_Logistics_Globals_Tunables.Manufacture.Weapon_Stock()))



                    ImGui.Separator()
                    ImGui.SeparatorText("RESEARCH")
                    ImGui.Text("    Current Research Index: " .. Disruption_Logistics_Globals_Tunables.Research.Current_Item())
                    ImGui.Text("    Current Research Level: " .. Disruption_Logistics_Globals_Tunables.Research.Research_Percentage() .. " / " .. Disruption_Logistics_Globals_Tunables.Research.Capacity())
                    


                    ImGui.Separator()
                    ImGui.SeparatorText("UPGRADES")
                    DL_Equipment_Addon = ImGui.Checkbox("Equipment", DL_Equipment_Addon)
                    DL_Staff_Addon = ImGui.Checkbox("Staff", DL_Staff_Addon)
                    DL_Security_Addon = ImGui.Checkbox("Security", DL_Security_Addon)
                    DL_Upgrades_Button = ImGui.Button("Confirm Upgrades")
                    if DL_Upgrades_Button then
                        if DL_Equipment_Addon then
                            stats.set_int(getMP() .. "BUNKER_EQUIPMENT", 1)
                        end
                        if DL_Staff_Addon then
                            stats.set_int(getMP() .. "BUNKER_STAFF", 1)
                        end
                        if DL_Security_Addon then
                            stats.set_int(getMP() .. "BUNKER_SECURITY", 1)
                        end
                        gui.show_message("Disruptive Logistics Upgrades Purchased!", "Awaiting Session Change")
                    end

                    ImGui.EndTabItem()
                end
            end





            if ImGui.BeginTabItem("The Open Road") then
                ImGui.SeparatorText("Master Control Terminal")
                Master_Control_Terminal = ImGui.Button("Access Business Management Portal")
                if Master_Control_Terminal then
                    SCRIPT.REQUEST_SCRIPT("apparcadebusinesshub")
                    SYSTEM.START_NEW_SCRIPT("apparcadebusinesshub", 8344)
                end




                MC_Globals = {
                    Capacity = { -- Source: am_mp_biker_warehouse.c
                        Counterfeit_Cash_Factory = function() return tunables.get_int("BIKER_COUNTERCASH_CAPACITY") end,
                        Cocaine_Lockup = function() return tunables.get_int("BIKER_CRACK_CAPACITY") end,
                        Document_Forgery_Office = function() return tunables.get_int("BIKER_FAKEIDS_CAPACITY") end,
                        Methamphetamine_Lab = function() return tunables.get_int("BIKER_METH_CAPACITY") end,
                        Weed_Farm = function() return tunables.get_int("BIKER_WEED_CAPACITY") end,
                    },
                    Product_Value = { -- Source: am_mp_biker_warehouse.c
                        Base = {
                            Counterfeit_Cash_Factory = function() return tunables.get_int("BIKER_COUNTERCASH_PRODUCT_VALUE") end,
                            Cocaine_Lockup = function() return tunables.get_int("BIKER_CRACK_PRODUCT_VALUE") end,
                            Document_Forgery_Office = function() return tunables.get_int("BIKER_FAKEIDS_PRODUCT_VALUE") end,
                            Methamphetamine_Lab = function() return tunables.get_int("BIKER_METH_PRODUCT_VALUE") end,
                            Weed_Farm = function() return tunables.get_int("BIKER_WEED_PRODUCT_VALUE") end
                        },
                        Equipment_Addon = {
                            Counterfeit_Cash_Factory = function() return tunables.get_int("BIKER_COUNTERCASH_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                            Cocaine_Lockup = function() return tunables.get_int("BIKER_CRACK_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                            Document_Forgery_Office = function() return tunables.get_int("BIKER_FAKEIDS_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                            Methamphetamine_Lab = function() return tunables.get_int("BIKER_METH_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                            Weed_Farm = function() return tunables.get_int("BIKER_WEED_PRODUCT_VALUE_EQUIPMENT_UPGRADE") end,
                            Bonus = function(name) return MC_Globals.Product_Value.Base[name]() / MC_Globals.Product_Value.Equipment_Addon[name]() end
                        },
                        Staff_Addon = {
                            Counterfeit_Cash_Factory = function() return tunables.get_int("BIKER_COUNTERCASH_PRODUCT_VALUE_STAFF_UPGRADE") end,
                            Cocaine_Lockup = function() return tunables.get_int("BIKER_CRACK_PRODUCT_VALUE_STAFF_UPGRADE") end,
                            Document_Forgery_Office = function() return tunables.get_int("BIKER_FAKEIDS_PRODUCT_VALUE_STAFF_UPGRADE") end,
                            Methamphetamine_Lab = function() return tunables.get_int("BIKER_METH_PRODUCT_VALUE_STAFF_UPGRADE") end,
                            Weed_Farm = function() return tunables.get_int("BIKER_WEED_PRODUCT_VALUE_STAFF_UPGRADE") end,
                            Bonus = function(name) return MC_Globals.Product_Value.Base[name]() / MC_Globals.Product_Value.Staff_Addon[name]() end
                        }
                    },
                    Production_Time = { -- Source: am_mp_biker_warehouse.c
                        Counterfeit_Cash_Factory = function() tunables.set_int("BIKER_COUNTERCASH_PRODUCTION_TIME", 0) end,
                        Cocaine_Lockup = function() tunables.set_int("BIKER_CRACK_PRODUCTION_TIME", 0) end,
                        Document_Forgery_Office = function() tunables.set_int("BIKER_FAKEIDS_PRODUCTION_TIME", 0) end,
                        Methamphetamine_Lab = function() tunables.set_int("BIKER_METH_PRODUCTION_TIME", 0) end,
                        Weed_Farm = function() tunables.set_int("BIKER_WEED_PRODUCTION_TIME", 0) end
                    },
                    Resupply = function(name) -- Source: Unknown
                        globals.set_int(1662873 + (MC_Factory.Property_Index(name) + 1), 1)
                    end
                }


                MC_Factory = {
                    is_Valid = function(name)
                        for Property_Index = 0, 4 do
                            for index = 1, #MC_Factory.Property_Indexes[name] do
                                if MC_Factory.Property_Indexes[name][index] == stats.get_int(getMP() .. "PROP_FAC_SLOT" .. Property_Index) then
                                    return true
                                end
                            end
                        end
                        return false
                    end,
                    Location = function(Property_Index)
                        Locations = {"Paleto Bay", "Mount Chillad", "Paleto Bay", "Paleto Bay", "Paleto Bay", "El Burro Heights", "Downtown Vinewood", "Morningwood", "Vespucci Canals", "Textile City", "Grand Senora Desert", "San Chianski Mountain Range", "Alamo Sea", "Grand Senora Desert", "Grapeseed", "Terminal", "Elysian Island", "Elysian Island", "Cypress Flats", "Elysian Island"}
                        return Locations[Property_Index]
                    end,
                    Products = {
                        Capacity = function(name)
                            return MC_Globals.Capacity[name]()
                        end,
                        Stock = function(name)
                            return stats.get_int(getMP() .. "PRODTOTALFORFACTORY" .. MC_Factory.Property_Index(name))
                        end,
                        Value = function(name)
                            return MC_Globals.Product_Value[name]()
                        end
                    },
                    Property = function(name)
                        if is_int(MC_Factory.Property_Index(name)) then
                            return stats.get_int(getMP() .. "PROP_FAC_SLOT" .. MC_Factory.Property_Index(name))
                        else
                            return MC_Factory.Property_Index(name)
                        end
                    end,
                    Property_Index = function(name)
                        for Property_Index = 0, 4 do
                            for index = 1, #MC_Factory.Property_Indexes[name] do
                                if MC_Factory.Property_Indexes[name][index] == stats.get_int(getMP() .. "PROP_FAC_SLOT" .. Property_Index) then
                                    return Property_Index
                                end
                            end
                        end
                        return false
                    end,
                    Property_Indexes = {
                        Counterfeit_Cash_Factory = {4, 9, 14, 19},
                        Cocaine_Lockup = {3, 8, 13, 18},
                        Document_Forgery_Office = {5, 10, 15, 20},
                        Methamphetamine_Lab = {1, 6, 1, 16},
                        Weed_Farm = {2, 7, 12, 17}
                    },
                    Supplies = function(name)
                        return stats.get_int(getMP() .. "MATTOTALFORFACTORY" .. MC_Factory.Property_Index(name))
                    end,
                    Upgrades = {
                        Equipment = function(name)
                            return stats.get_int(getMP() .. "FACTORYUPGRADES" .. MC_Factory.Property_Index(name))
                        end,
                        Staff = function(name)
                            return stats.get_int(getMP() .. "FACTORYUPGRADES" .. MC_Factory.Property_Index(name) .. "_1")
                        end
                    }
                }



                ImGui.Separator()
                ImGui.SeparatorText("MANUFACTURES")
                if ImGui.TreeNode("Counterfeit Cash Factory") then
                    ImGui.Text("    Supplies Level: " .. MC_Factory.Supplies("Counterfeit_Cash_Factory"))
                    ImGui.Text("    Stock Level: " .. MC_Factory.Products.Stock("Counterfeit_Cash_Factory") .. " / " .. MC_Globals.Capacity.Counterfeit_Cash_Factory())

                    if MC_Factory.Upgrades.Equipment("Counterfeit_Cash_Factory") == 1 and MC_Factory.Upgrades.Staff("Counterfeit_Cash_Factory") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Counterfeit_Cash_Factory() + MC_Globals.Product_Value.Equipment_Addon.Counterfeit_Cash_Factory() + MC_Globals.Product_Value.Staff_Addon.Counterfeit_Cash_Factory()
                    elseif MC_Factory.Upgrades.Equipment("Counterfeit_Cash_Factory") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Counterfeit_Cash_Factory() + MC_Globals.Product_Value.Equipment_Addon.Counterfeit_Cash_Factory()
                    elseif MC_Factory.Upgrades.Staff("Counterfeit_Cash_Factory") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Counterfeit_Cash_Factory() + MC_Globals.Product_Value.Staff_Addon.Counterfeit_Cash_Factory()
                    else
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Counterfeit_Cash_Factory()
                    end
                    ImGui.Text("    Stock Price: $" .. format_Number(MC_CCF_PPU * MC_Factory.Products.Stock("Counterfeit_Cash_Factory")))
                    
                    MC_CCF_PT = ImGui.Button("Start Production")
                    if MC_CCF_PT then
                        MC_Globals.Production_Time.Counterfeit_Cash_Factory()
                    end
                    ImGui.TreePop()
                end


                if ImGui.TreeNode("Cocaine Lockup") then
                    ImGui.Text("    Supplies Level: " .. MC_Factory.Supplies("Cocaine_Lockup"))
                    ImGui.Text("    Stock Level: " .. MC_Factory.Products.Stock("Cocaine_Lockup") .. " / " .. MC_Globals.Capacity.Cocaine_Lockup())

                    if MC_Factory.Upgrades.Equipment("Cocaine_Lockup") == 1 and MC_Factory.Upgrades.Staff("Cocaine_Lockup") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Cocaine_Lockup() + MC_Globals.Product_Value.Equipment_Addon.Cocaine_Lockup() + MC_Globals.Product_Value.Staff_Addon.Cocaine_Lockup()
                    elseif MC_Factory.Upgrades.Equipment("Cocaine_Lockup") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Cocaine_Lockup() + MC_Globals.Product_Value.Equipment_Addon.Cocaine_Lockup()
                    elseif MC_Factory.Upgrades.Staff("Cocaine_Lockup") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Cocaine_Lockup() + MC_Globals.Product_Value.Staff_Addon.Cocaine_Lockup()
                    else
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Cocaine_Lockup()
                    end
                    ImGui.Text("    Stock Price: $" .. format_Number(MC_CCF_PPU * MC_Factory.Products.Stock("Cocaine_Lockup")))
                    
                    MC_CCF_PT = ImGui.Button("Start Production")
                    if MC_CCF_PT then
                        MC_Globals.Production_Time.Cocaine_Lockup()
                    end
                    ImGui.TreePop()
                end


                if ImGui.TreeNode("Document Fogery Office") then
                    ImGui.Text("    Supplies Level: " .. MC_Factory.Supplies("Document_Forgery_Office"))
                    ImGui.Text("    Stock Level: " .. MC_Factory.Products.Stock("Document_Forgery_Office") .. " / " .. MC_Globals.Capacity.Document_Forgery_Office())

                    if MC_Factory.Upgrades.Equipment("Document_Forgery_Office") == 1 and MC_Factory.Upgrades.Staff("Document_Forgery_Office") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Document_Forgery_Office() + MC_Globals.Product_Value.Equipment_Addon.Document_Forgery_Office() + MC_Globals.Product_Value.Staff_Addon.Document_Forgery_Office()
                    elseif MC_Factory.Upgrades.Equipment("Document_Forgery_Office") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Document_Forgery_Office() + MC_Globals.Product_Value.Equipment_Addon.Document_Forgery_Office()
                    elseif MC_Factory.Upgrades.Staff("Document_Forgery_Office") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Document_Forgery_Office() + MC_Globals.Product_Value.Staff_Addon.Document_Forgery_Office()
                    else
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Document_Forgery_Office()
                    end
                    ImGui.Text("    Stock Price: $" .. format_Number(MC_CCF_PPU * MC_Factory.Products.Stock("Document_Forgery_Office")))
                    
                    MC_CCF_PT = ImGui.Button("Start Production")
                    if MC_CCF_PT then
                        MC_Globals.Production_Time.Document_Forgery_Office()
                    end
                    ImGui.TreePop()
                end


                if ImGui.TreeNode("Methamphetamine Lab") then
                    ImGui.Text("    Supplies Level: " .. MC_Factory.Supplies("Methamphetamine_Lab"))
                    ImGui.Text("    Stock Level: " .. MC_Factory.Products.Stock("Methamphetamine_Lab") .. " / " .. MC_Globals.Capacity.Methamphetamine_Lab())

                    if MC_Factory.Upgrades.Equipment("Methamphetamine_Lab") == 1 and MC_Factory.Upgrades.Staff("Cocaine_Lockup") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Methamphetamine_Lab() + MC_Globals.Product_Value.Equipment_Addon.Methamphetamine_Lab() + MC_Globals.Product_Value.Staff_Addon.Methamphetamine_Lab()
                    elseif MC_Factory.Upgrades.Equipment("Methamphetamine_Lab") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Methamphetamine_Lab() + MC_Globals.Product_Value.Equipment_Addon.Methamphetamine_Lab()
                    elseif MC_Factory.Upgrades.Staff("Methamphetamine_Lab") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Methamphetamine_Lab() + MC_Globals.Product_Value.Staff_Addon.Methamphetamine_Lab()
                    else
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Methamphetamine_Lab()
                    end
                    ImGui.Text("    Stock Price: $" .. format_Number(MC_CCF_PPU * MC_Factory.Products.Stock("Methamphetamine_Lab")))
                    
                    MC_CCF_PT = ImGui.Button("Start Production")
                    if MC_CCF_PT then
                        MC_Globals.Production_Time.Methamphetamine_Lab()
                    end
                    ImGui.TreePop()
                end


                if ImGui.TreeNode("Weed Farm") then
                    ImGui.Text("    Supplies Level: " .. MC_Factory.Supplies("Weed_Farm"))
                    ImGui.Text("    Stock Level: " .. MC_Factory.Products.Stock("Weed_Farm") .. " / " .. MC_Globals.Capacity.Weed_Farm())

                    if MC_Factory.Upgrades.Equipment("Weed_Farm") == 1 and MC_Factory.Upgrades.Staff("Cocaine_Lockup") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Weed_Farm() + MC_Globals.Product_Value.Equipment_Addon.Weed_Farm() + MC_Globals.Product_Value.Staff_Addon.Weed_Farm()
                    elseif MC_Factory.Upgrades.Equipment("Weed_Farm") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Weed_Farm() + MC_Globals.Product_Value.Equipment_Addon.Weed_Farm()
                    elseif MC_Factory.Upgrades.Staff("Weed_Farm") == 1 then
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Weed_Farm() + MC_Globals.Product_Value.Staff_Addon.Weed_Farm()
                    else
                        MC_CCF_PPU = MC_Globals.Product_Value.Base.Weed_Farm()
                    end
                    ImGui.Text("    Stock Price: $" .. format_Number(MC_CCF_PPU * MC_Factory.Products.Stock("Weed_Farm")))
                    
                    MC_CCF_PT = ImGui.Button("Start Production")
                    if MC_CCF_PT then
                        MC_Globals.Production_Time.Weed_Farm()
                    end
                    ImGui.TreePop()
                end

                ImGui.EndTabItem()
            end
            


            if ImGui.BeginTabItem("Underground Nightclub") then
                ImGui.SeparatorText("Master Control Terminal")
                Master_Control_Terminal = ImGui.Button("Access Business Management Portal")
                if Master_Control_Terminal then
                    SCRIPT.REQUEST_SCRIPT("apparcadebusinesshub")
                    SYSTEM.START_NEW_SCRIPT("apparcadebusinesshub", 8344)
                end



                -- Source: am_mp_business_hub.c --
                local Underground_Nightclub_Tunables = {
                    Products = {
                        Capacity = {
                            Sporting_Goods = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_WEAPONS") end,
                            South_American_Imports = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_COKE") end,
                            Pharmaceutical_Research = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_METH") end,
                            Organic_Produce = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_WEED") end,
                            Printing_and_Copying = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_FORGED_DOCUMENTS") end,
                            Cash_Creation = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_COUNTERFEIT_CASH") end,
                            Cargo_and_Shipment = function() return tunables.get_int("BB_BUSINESS_TOTAL_MAX_UNITS_CARGO") end
                        },
                        Stock = {
                            Cargo_and_Shipment = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_0") end,
                            Sporting_Goods = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_1") end,
                            South_American_Imports = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_2") end,
                            Pharmaceutical_Research = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_3") end,
                            Organic_Produce = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_4") end,
                            Printing_and_Copying = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_5") end,
                            Cash_Creation = function() return stats.get_int(getMP() .. "HUB_PROD_TOTAL_6") end
                        },
                        Value = {
                            Sporting_Goods = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_WEAPONS") end,
                            South_American_Imports = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_COKE") end,
                            Pharmaceutical_Research = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_METH") end,
                            Organic_Produce = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_WEED") end,
                            Printing_and_Copying = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_FORGED_DOCUMENTS") end,
                            Cash_Creation = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_COUNTERFEIT_CASH") end,
                            Cargo_and_Shipment = function() return tunables.get_int("BB_BUSINESS_BASIC_VALUE_CARGO") end
                        }
                    },
                    DJ = {
                        New_Bookings = {
                            Dixon = function() tunables.get_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_DIXON") end,
                            Tale_Of_Us = function() tunables.get_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_TALE_OF_US") end,
                            Black_Madonna = function() tunables.get_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_THE_BLACK_MADONNA") end
                        },
                        Rebooking = {
                            Solomon = function() tunables.get_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_SOLOMUN") end,
                            Dixon = function() tunables.get_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_DIXON") end,
                            Tale_Of_Us = function() tunables.get_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_TALE_OF_US") end,
                            Black_Madonna = function() tunables.get_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_THE_BLACK_MADONNA") end
                        }
                    }
                }
                
                
                ImGui.Separator()
                ImGui.SeparatorText("MANUFACTURES")
                if ImGui.TreeNode("CARGO & SHIPMENT") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Cargo_and_Shipment() .. " / 10")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Cargo_and_Shipment() * Underground_Nightclub_Tunables.Products.Value.Cargo_and_Shipment()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("SPORTING GOODS") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Sporting_Goods() .. " / 20")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Sporting_Goods() * Underground_Nightclub_Tunables.Products.Value.Sporting_Goods()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("SOUTH AMERICAN IMPORTS") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.South_American_Imports() .. " / 2")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.South_American_Imports() * Underground_Nightclub_Tunables.Products.Value.South_American_Imports()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("PHARMACEUTICAL RESEARCH") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Pharmaceutical_Research() .. " / 4")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Pharmaceutical_Research() * Underground_Nightclub_Tunables.Products.Value.Pharmaceutical_Research()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("ORGANIC PRODUCE") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Organic_Produce() .. " / 16")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Organic_Produce() * Underground_Nightclub_Tunables.Products.Value.Organic_Produce()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("PRINTING & COPYING") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Printing_and_Copying() .. " / 12")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Printing_and_Copying() * Underground_Nightclub_Tunables.Products.Value.Printing_and_Copying()))
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("CASH CREATION") then
                    ImGui.Text("    Stock Level: " .. Underground_Nightclub_Tunables.Products.Stock.Cash_Creation() .. " / 8")
                    ImGui.Text("    Stock Price: $" .. format_Number(Underground_Nightclub_Tunables.Products.Stock.Cash_Creation() * Underground_Nightclub_Tunables.Products.Value.Cash_Creation()))
                    ImGui.TreePop()
                end



                ImGui.Separator()
                ImGui.SeparatorText("Resident DJ")

                NightClub_DJ_Pricing_Discount = ImGui.Button("100% Discount")
                if NightClub_DJ_Pricing_Discount then
                    tunables.set_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_DIXON", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_TALE_OF_US", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_INITIAL_DJ_COST_THE_BLACK_MADONNA", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_SOLOMUN", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_DIXON", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_TALE_OF_US", 0)
                    tunables.set_int("BB_NIGHTCLUB_APP_DJ_REBOOKING_COST_THE_BLACK_MADONNA", 0)
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Applies 100% discount to all new booking and rebooking prices for DJs.")
                end

                ImGui.EndTabItem()
            end
        end
    else
        ImGui.Text("Not available in singleplayer.")
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------





------------------------------------------------------------------------------------------------------------------------------------------------------
Heist_Manager = menu:add_tab(" - Heist Editor")
Heist_Manager:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar("- Heist Editor") then

            if ImGui.BeginTabItem("Apartment") then
                ImGui.SeparatorText("PREPERATION")
                Apartment_Heist_Prep_Skip = ImGui.Button("Skip Current Apartment Heist Preps")
                if Apartment_Heist_Prep_Skip then
                    stats.set_int(getMP() .. "HEIST_PLANNING_STAGE", -1)
                end
                
                Apartment_Heist_Prep_Reset = ImGui.Button("Reset Current Apartment Heist Preps")
                if Apartment_Heist_Prep_Reset then
                    stats.set_int(getMP() .. "HEIST_PLANNING_STAGE", 0)
                end


                ImGui.Separator()
                ImGui.SeparatorText("CUTS")
                Apartment_Heist_Fleeca_Cut = ImGui.Button("Fleeca Heist Cuts")
                if Apartment_Heist_Fleeca_Cut then
                    globals.set_int(1929317 + 1 + 1, -200)
                    globals.set_int(1929317 + 1 + 2, 100)
                end
                
                Apartment_Heist_Non_Fleeca_Cut = ImGui.Button("Non-Fleeca Heist Cuts")
                if Apartment_Heist_Non_Fleeca_Cut then
                    globals.set_int(1929317 + 1 + 1, -200)
                    globals.set_int(1929317 + 1 + 2, 100)
                    globals.set_int(1929317 + 1 + 3, 100)
                    globals.set_int(1929317 + 1 + 4, 100)
                end

                if ImGui.TreeNode("During Heist") then
                    Apartment_Heist_Fleeca_Hack = ImGui.Button("Fleeca Bypass Hack")
                    if Apartment_Heist_Fleeca_Hack then
                        locals.set_int("fm_mission_controller", 11812 + 24, 7)
                    end
                    Apartment_Heist_Fleeca_Drill = ImGui.Button("Fleeca Bypass Drill")
                    if Apartment_Heist_Fleeca_Drill then
                        locals.set_float("fm_mission_controller", 10143 + 11, 100)
                    end
                    ImGui.TreePop()
                end

                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Casino") then
                ImGui.SeparatorText("* ACCESS POINT *")
                DCH_ScopeAccessPoint = ImGui.Button("Scope all Access Points")
                if DCH_ScopeAccessPoint then
                    stats.set_int(getMP() .. "H3OPT_POI", -1)
                    stats.set_int(getMP() .. "H3OPT_ACCESSPOINTS", -1)
                end
                ImGui.Separator()


                ImGui.SeparatorText("* TARGET *")
                if ImGui.TreeNode("Primary Target") then
                    Casino_Diamond_Target = ImGui.Checkbox("Diamonds", Casino_Diamond_Target)
                    if Casino_Diamond_Target then
                        Casino_Gold_Target = false
                        Casino_Arts_Target = false
                        Casino_Cash_Target = false
                    end
                    Casino_Gold_Target = ImGui.Checkbox("Gold", Casino_Gold_Target)
                    if Casino_Gold_Target then
                        Casino_Diamond_Target = false
                        Casino_Arts_Target = false
                        Casino_Cash_Target = false
                    end
                    Casino_Arts_Target = ImGui.Checkbox("Arts", Casino_Arts_Target)
                    if Casino_Arts_Target then
                        Casino_Diamond_Target = false
                        Casino_Gold_Target = false
                        Casino_Cash_Target = false
                    end
                    Casino_Cash_Target = ImGui.Checkbox("Cash", Casino_Cash_Target)
                    if Casino_Cash_Target then
                        Casino_Diamond_Target = false
                        Casino_Gold_Target = false
                        Casino_Arts_Target = false
                    end


                    Casino_Target_Button = ImGui.Button("Confirm Target")
                    if Casino_Target_Button then
                        if Casino_Diamond_Target then
                            stats.set_int(getMP() .. "H3OPT_TARGET", 3)
                        elseif Casino_Gold_Target then
                            stats.set_int(getMP() .. "H3OPT_TARGET", 1)
                        elseif Casino_Arts_Target then
                            stats.set_int(getMP() .. "H3OPT_TARGET", 2)
                        elseif Casino_Cash_Target then
                            stats.set_int(getMP() .. "H3OPT_TARGET", 0)
                        end
                    end

                    ImGui.TreePop()
                end
                ImGui.Separator()


                ImGui.SeparatorText("* SELECT APPROACH *")
                if ImGui.TreeNode("Approach") then
                    Casino_SilentAndSneaky_Approach = ImGui.Checkbox("Silent & Sneaky", Casino_SilentAndSneaky_Approach)
                    if Casino_SilentAndSneaky_Approach then
                        Casino_TheBigCon_Approach = false
                        Casino_Aggressive_Approach = false
                    end
                    Casino_TheBigCon_Approach = ImGui.Checkbox("The Big Con", Casino_TheBigCon_Approach)
                    if Casino_TheBigCon_Approach then
                        Casino_SilentAndSneaky_Approach = false
                        Casino_Aggressive_Approach = false
                    end
                    Casino_Aggressive_Approach = ImGui.Checkbox("Aggressive", Casino_Aggressive_Approach)
                    if Casino_Aggressive_Approach then
                        Casino_SilentAndSneaky_Approach = false
                        Casino_TheBigCon_Approach = false
                    end


                    Casino_Approach_Button = ImGui.Button("Confirm Approach")
                    if Casino_Approach_Button then
                        if Casino_SilentAndSneaky_Approach then
                            stats.set_int(getMP() .. "H3OPT_APPROACH", 1)
                        elseif Casino_TheBigCon_Approach then
                            stats.set_int(getMP() .. "H3OPT_APPROACH", 2)
                        elseif Casino_Aggressive_Approach then
                            stats.set_int(getMP() .. "H3OPT_APPROACH", 3)
                        end
                    end

                    ImGui.TreePop()
                end
                ImGui.Separator()


                ImGui.SeparatorText("* SUPPORT CREW *")
                if ImGui.TreeNode("Gunman Options") then
                    if ImGui.TreeNode("Chester McCoy") then
                        DCH_Gunman_Chester_McCoy1 = ImGui.Checkbox("Option: 1", DCH_Gunman_Chester_McCoy1)
                        if DCH_Gunman_Chester_McCoy1 then
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: Silent & Sneaky\nEquipment:\n - Pump Shotgun MK II (Silenced)\n - Pistol .50 (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: The Big Con\nEquipment:\n - SMG Mk II\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: Aggressive\nEquipment:\n - Pump Shotgun Mk II\n - SMG Mk II\n - Pipe Bombs\n - Pipe Wrench\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        DCH_Gunman_Chester_McCoy2 = ImGui.Checkbox("Option: 2", DCH_Gunman_Chester_McCoy2)
                        if DCH_Gunman_Chester_McCoy2 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: Silent & Sneaky\nEquipment:\n - Carbine Rifle Mk II (Silenced)\n - Pistol .50 (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: The Big Con\nEquipment:\n - Bullpup Rifle Mk II\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 10%\nApproach: Aggressive\nEquipment:\n - Assault Rifle Mk II\n - SMG Mk II\n - Pipe Bombs\n - Pipe Wrench\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        ImGui.TreePop()
                    end
                    if ImGui.TreeNode("Gustavo Mota") then
                        DCH_Gunman_Gustavo_Mota1 = ImGui.Checkbox("Option: 1", DCH_Gunman_Gustavo_Mota1)
                        if DCH_Gunman_Gustavo_Mota1 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: Silent & Sneaky\nEquipment:\n - Carbine Rifle (Silenced)\n - Heavy Pistol (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: The Big Con\nEquipment:\n - Carbine Rifle\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: Aggressive\nEquipment:\n - Carbine Rifle\n - SMG\n - Proximity Mines\n - Machete\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        DCH_Gunman_Gustavo_Mota2 = ImGui.Checkbox("Option: 2", DCH_Gunman_Gustavo_Mota2)
                        if DCH_Gunman_Gustavo_Mota2 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: Silent & Sneaky\nEquipment:\n - Assault Shotgun (Silenced)\n - Pistol .50 (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: The Big Con\nEquipment:\n - Assault Shotgun\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Expert\nCut: 9%\nApproach: Aggressive\nEquipment:\n - Assault Shotgun\n - SMG\n - Proximity Mines\n - Machete\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        ImGui.TreePop()
                    end
                    if ImGui.TreeNode("Patrick McReary") then
                        DCH_Gunman_Patrick_McReary1 = ImGui.Checkbox("Option: 1", DCH_Gunman_Patrick_McReary1)
                        if DCH_Gunman_Patrick_McReary1 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: Silent & Sneaky\nEquipment:\n - Combat PDW\n - Pistol .50 (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: The Big Con\nEquipment:\n - Sawed-Off Shotgun\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: Aggressive\nEquipment:\n - Heavy Shotgun\n - SMG\n - Sticky Bombs\n - Crowbar\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        DCH_Gunman_Patrick_McReary2 = ImGui.Checkbox("Option: 2", DCH_Gunman_Patrick_McReary2)
                        if DCH_Gunman_Patrick_McReary2 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: Silent & Sneaky\nEquipment:\n - Assault Rifle (Silenced)\n - Pistol .50 (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: The Big Con\nEquipment:\n - Compact Rifle\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Good\nCut: 8%\nApproach: Aggressive\nEquipment:\n - Combat MG\n - SMG\n - Sticky Bombs\n - Crowbar\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        ImGui.TreePop()
                    end
                    if ImGui.TreeNode("Charlie Reed") then
                        DCH_Gunman_Charlie_Reed1 = ImGui.Checkbox("Option: 1", DCH_Gunman_Charlie_Reed1)
                        if DCH_Gunman_Charlie_Reed1 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: Silent & Sneaky\nEquipment:\n - Assault SMG (Silenced)\n - Combat Pistol (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: The Big Con\nEquipment:\n - Machine Pistol\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: Aggressive\nEquipment:\n - Assault SMG\n - SMG\n - Grenades\n - Hammer\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        DCH_Gunman_Charlie_Reed2 = ImGui.Checkbox("Option: 2", DCH_Gunman_Charlie_Reed2)
                        if DCH_Gunman_Charlie_Reed2 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: Silent & Sneaky\nEquipment:\n - Bullpup Shotgun (Silenced)\n - Heavy Pistol (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: The Big Con\nEquipment:\n - Sweeper Shotgun\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Good\nCut: 7%\nApproach: Aggressive\nEquipment:\n - Pump Shotgun\n - SMG\n - Grenades\n - Hammer\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        ImGui.TreePop()
                    end
                    if ImGui.TreeNode("Karl Abolaji") then
                        DCH_Gunman_Karl_Abolaji1 = ImGui.Checkbox("Option: 1", DCH_Gunman_Karl_Abolaji1)
                        if DCH_Gunman_Karl_Abolaji1 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji2 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: Silent & Sneaky\nEquipment:\n - Micro SMG (Silenced)\n - Vintage Pistol (Silenced)\n - Stun Gun\n - Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: The Big Con\nEquipment:\n - Micro SMG\n - Ceramic Pistol\n - Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: Aggressive\nEquipment:\n - Sawed-Off Shotgun\n - SMG\n - Molotov Cocktails\n - Knuckledusters\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        DCH_Gunman_Karl_Abolaji2 = ImGui.Checkbox("Option: 2", DCH_Gunman_Karl_Abolaji2)
                        if DCH_Gunman_Karl_Abolaji2 then
                            DCH_Gunman_Chester_McCoy1 = false
                            DCH_Gunman_Chester_McCoy2 = false
                            DCH_Gunman_Gustavo_Mota1 = false
                            DCH_Gunman_Gustavo_Mota2 = false
                            DCH_Gunman_Patrick_McReary1 = false
                            DCH_Gunman_Patrick_McReary2 = false
                            DCH_Gunman_Charlie_Reed1 = false
                            DCH_Gunman_Charlie_Reed2 = false
                            DCH_Gunman_Karl_Abolaji1 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            if stats.get_int(getMP() .. "H3OPT_APPROACH") == 1 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: Silent & Sneaky\nEquipment:\n - Primary Weapon: Machine Pistol (Silenced)\n - Secondary Weapon: Combat Pistol (Silenced)\n - Stun Gun\n - Melee: Knife\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 2 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: The Big Con\nEquipment:\n - Primary Weapon: Double Barrel Shotgun\n - Secondary Weapon: Ceramic Pistol\n - Melee: Switchblade\n\nNote: Equipment details will change base on the chosen approach.")
                            elseif stats.get_int(getMP() .. "H3OPT_APPROACH") == 3 then
                                ImGui.SetTooltip("Skill: Poor\nCut: 5%\nApproach: Aggressive\nEquipment:\n - Primary Weapon: Heavy Revolver\n - Secondary Weapon: SMG\n - Throwables: Molotov Cocktails\n - Melee: Knuckledusters\n\nNote: Equipment details will change base on the chosen approach.")
                            end
                        end
                        ImGui.TreePop()
                    end
                    DCH_Confirm_Gunman_Button = ImGui.Button("Confirm Gunman")
                    if DCH_Confirm_Gunman_Button then
                        if DCH_Gunman_Karl_Abolaji1 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 1)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 0)
                        elseif DCH_Gunman_Karl_Abolaji2 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 1)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 1)
                        elseif DCH_Gunman_Gustavo_Mota1 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 2)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 0)
                        elseif DCH_Gunman_Gustavo_Mota2 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 2)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 1)
                        elseif DCH_Gunman_Charlie_Reed1 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 3)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 0)
                        elseif DCH_Gunman_Charlie_Reed2 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 3)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 1)
                        elseif DCH_Gunman_Chester_McCoy1 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 4)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 0)
                        elseif DCH_Gunman_Chester_McCoy2 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 4)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 1)
                        elseif DCH_Gunman_Patrick_McReary1 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 5)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 0)
                        elseif DCH_Gunman_Patrick_McReary2 then
                            stats.set_int(getMP() .. "H3OPT_CREWWEAP", 5)
                            stats.set_int(getMP() .. "H3OPT_WEAPS", 1)
                        end
                        
                        locals.set_int("gb_casino_heist_planning", DCRBl, 2)
                    end
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("Driver Options") then      
                    if ImGui.TreeNode("Karim Denz") then
                        DCH_Driver_Karim_Denz1 = ImGui.Checkbox("Weeny 'Issi Classic'", DCH_Driver_Karim_Denz1)
                        if DCH_Driver_Karim_Denz1 then
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Poor\nCut: 5%\nStatistics:\n - Speed: 67.07/100\n - Acceleration: 65.00/100\n - Braking: 10.00/100\n - Handling: 60.61/100\n - Drive Train: FWD\n - Seats: 2")
                        end
                        DCH_Driver_Karim_Denz2 = ImGui.Checkbox("Maxwell 'Asbo'", DCH_Driver_Karim_Denz2)
                        if DCH_Driver_Karim_Denz2 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Poor\nCut: 5%\nStatistics:\n - Speed: 67.61/100\n - Acceleration: 58.50/100\n - Braking: 15.67/100\n - Handling: 58.18/100\n - Drive Train: FWD\n - Seats: 2")
                        end
                        DCH_Driver_Karim_Denz3 = ImGui.Checkbox("Dinka Blista Kanjo", DCH_Driver_Karim_Denz3)
                        if DCH_Driver_Karim_Denz3 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Poor\nCut: 5%\nStatistics:\n - Speed: 75.12/100\n - Acceleration: 80.00/100\n - Braking: 16.67/100\n - Handling: 59.70/100\n - Drive Train: FWD\n - Seats: 2")
                        end
                        DCH_Driver_Karim_Denz4 = ImGui.Checkbox("Übermacht 'Sentinel Classic'", DCH_Driver_Karim_Denz4)
                        if DCH_Driver_Karim_Denz4 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Poor\nCut: 5%\nStatistics:\n - Speed: 75.12/100\n - Acceleration: 66.25/100\n - Braking: 26.67/100\n - Handling: 68.18/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        ImGui.TreePop()
                    end

                    
                    if ImGui.TreeNode("Taliana Martinez") then
                        DCH_Driver_Taliana_Martinez1 = ImGui.Checkbox("Vapid 'Retinue Mk II'", DCH_Driver_Taliana_Martinez1)
                        if DCH_Driver_Taliana_Martinez1 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 7%\nStatistics:\n - Speed: 77.80/100\n - Acceleration: 69.38/100\n - Braking: 24.00/100\n - Handling: 62.12/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Taliana_Martinez2 = ImGui.Checkbox("Declasse 'Drift Yosemite'", DCH_Driver_Taliana_Martinez2)
                        if DCH_Driver_Taliana_Martinez2 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 7%\nStatistics:\n - Speed: 75.12/100\n - Acceleration: 98.75/100\n - Braking: 28.33/100\n - Handling: 79.55/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Taliana_Martinez3 = ImGui.Checkbox("Dinka 'Sugoi'", DCH_Driver_Taliana_Martinez3)
                        if DCH_Driver_Taliana_Martinez3 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 7%\nStatistics:\n - Speed: 83.70/100\n - Acceleration: 77.50/100\n - Braking: 28.33/100\n - Handling: 100/100\n - Drive Train: FWD\n - Seats: 4")
                        end
                        DCH_Driver_Taliana_Martinez4 = ImGui.Checkbox("Ocelot 'Jugular'", DCH_Driver_Taliana_Martinez4)
                        if DCH_Driver_Taliana_Martinez4 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 7%\nStatistics:\n - Speed: 84.51/100\n - Acceleration: 94.50/100\n - Braking: 36.67/100\n - Handling: 100/100\n - Drive Train: AWD\n - Seats: 4")
                        end
                        ImGui.TreePop()
                    end

                    
                    if ImGui.TreeNode("Eddie Toh") then
                        DCH_Driver_Eddie_Toh1 = ImGui.Checkbox("Karin 'Sultan Classic'", DCH_Driver_Eddie_Toh1)
                        if DCH_Driver_Eddie_Toh1 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 9%\nStatistics:\n - Speed: 77.80/100\n - Acceleration: 82.50/100\n - Braking: 16.67/100\n - Handling: 75.61/100\n - Drive Train: AWD\n - Seats: 4")
                        end
                        DCH_Driver_Eddie_Toh2 = ImGui.Checkbox("Bravado 'Gauntlet Classic'", DCH_Driver_Eddie_Toh2)
                        if DCH_Driver_Eddie_Toh2 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 9%\nStatistics:\n - Speed: 76.19/100\n - Acceleration: 70.00/100\n - Braking: 30.00/100\n - Handling: 75.76/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Eddie_Toh3 = ImGui.Checkbox("Vapid 'Ellie'", DCH_Driver_Eddie_Toh3)
                        if DCH_Driver_Eddie_Toh3 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 9%\nStatistics:\n - Speed: 75.39/100\n - Acceleration: 81.25/100\n - Braking: 16.67/100\n - Handling: 77.27/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Eddie_Toh4 = ImGui.Checkbox("Lampadati 'Komoda'", DCH_Driver_Eddie_Toh4)
                        if DCH_Driver_Eddie_Toh4 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 9%\nStatistics:\n - Speed: 83.70/100\n - Acceleration: 91.75/100\n - Braking: 31.67/100\n - Handling: 81.52/100\n - Drive Train: RWD\n - Seats: 4")
                        end
                        ImGui.TreePop()
                    end

                    
                    if ImGui.TreeNode("Zach Nelson") then
                        DCH_Driver_Zach_Nelson1 = ImGui.Checkbox("Maibatsu 'Manchez'", DCH_Driver_Zach_Nelson1)
                        if DCH_Driver_Zach_Nelson1 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 6%\nStatistics:\n - Speed: 77.80/100\n - Acceleration: 73.75/100\n - Braking: 40.00/100\n - Handling: 65.15/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Zach_Nelson2 = ImGui.Checkbox("Nagasaki 'Stryder'", DCH_Driver_Zach_Nelson2)
                        if DCH_Driver_Zach_Nelson2 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 6%\nStatistics:\n - Speed: 69.75/100\n - Acceleration: 90.00/100\n - Braking: 40.00/100\n - Handling: 74.24/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Zach_Nelson3 = ImGui.Checkbox("Shitzu 'Defiler'", DCH_Driver_Zach_Nelson3)
                        if DCH_Driver_Zach_Nelson3 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 6%\nStatistics:\n - Speed: 79.41/100\n - Acceleration: 100/100\n - Braking: 40.00/100\n - Handling: 65.15/100\n - Drive Train: RWD\n - Seats: 1")
                        end
                        DCH_Driver_Zach_Nelson4 = ImGui.Checkbox("Principe 'Lectro'", DCH_Driver_Zach_Nelson4)
                        if DCH_Driver_Zach_Nelson4 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Good\nCut: 6%\nStatistics:\n - Speed: 75.12/100\n - Acceleration: 70.00/100\n - Braking: 40.00/100\n - Handling: 59.09/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        ImGui.TreePop()
                    end


                    if ImGui.TreeNode("Chester McCoy") then
                        DCH_Driver_Chester_McCoy1 = ImGui.Checkbox("RUNE 'Zhaba'", DCH_Driver_Chester_McCoy1)
                        if DCH_Driver_Chester_McCoy1 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 10%\nStatistics:\n - Speed: 49.63/100\n - Acceleration: 45.00/100\n - Braking: 26.67/100\n - Handling: 57.58/100\n - Drive Train: AWD\n - Seats: 4")
                        end
                        DCH_Driver_Chester_McCoy2 = ImGui.Checkbox("Maxwell 'Vagrant'", DCH_Driver_Chester_McCoy2)
                        if DCH_Driver_Chester_McCoy2 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy3 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 10%\nStatistics:\n - Speed: 80.29/100\n - Acceleration: 83.13/100\n - Braking: 20.83/100\n - Handling: 71.21/100\n - Drive Train: RWD\n - Seats: 2")
                        end
                        DCH_Driver_Chester_McCoy3 = ImGui.Checkbox("Nagasaki 'Outlaw'", DCH_Driver_Chester_McCoy3)
                        if DCH_Driver_Chester_McCoy3 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy4 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 10%\nStatistics:\n - Speed: 62.78/100\n - Acceleration: 100/100\n - Braking: 20.00/100\n - Handling: 61.36/100\n - Drive Train: AWD\n - Seats: 2")
                        end
                        DCH_Driver_Chester_McCoy4 = ImGui.Checkbox("Karin 'Everon'", DCH_Driver_Chester_McCoy4)
                        if DCH_Driver_Chester_McCoy4 then
                            DCH_Driver_Karim_Denz1 = false
                            DCH_Driver_Karim_Denz2 = false
                            DCH_Driver_Karim_Denz3 = false
                            DCH_Driver_Karim_Denz4 = false
                            DCH_Driver_Taliana_Martinez1 = false
                            DCH_Driver_Taliana_Martinez2 = false
                            DCH_Driver_Taliana_Martinez3 = false
                            DCH_Driver_Taliana_Martinez4 = false
                            DCH_Driver_Eddie_Toh1 = false
                            DCH_Driver_Eddie_Toh2 = false
                            DCH_Driver_Eddie_Toh3 = false
                            DCH_Driver_Eddie_Toh4 = false
                            DCH_Driver_Zach_Nelson1 = false
                            DCH_Driver_Zach_Nelson2 = false
                            DCH_Driver_Zach_Nelson3 = false
                            DCH_Driver_Zach_Nelson4 = false
                            DCH_Driver_Chester_McCoy1 = false
                            DCH_Driver_Chester_McCoy2 = false
                            DCH_Driver_Chester_McCoy3 = false
                        end
                        ImGui.SameLine()
                        ImGui.TextDisabled("(?)")
                        if ImGui.IsItemHovered() then
                            ImGui.SetTooltip("Skill: Expert\nCut: 10%\nStatistics:\n - Speed: 72.97/100\n - Acceleration: 73.75/100\n - Braking: 10.00/100\n - Handling: 62.12/100\n - Drive Train: AWD\n - Seats: 4")
                        end
                        ImGui.TreePop()
                    end
                    

                    Getaway_Vehicle_Button = ImGui.Button("Confirm Getaway Vehicle")
                    if Getaway_Vehicle_Button then
                        if DCH_Driver_Karim_Denz1 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 1)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 0)
                        elseif DCH_Driver_Karim_Denz2 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 1)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 1)
                        elseif DCH_Driver_Karim_Denz3 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 1)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 2)
                        elseif DCH_Driver_Karim_Denz4 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 1)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 3)
                        elseif DCH_Driver_Taliana_Martinez1 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 2)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 0)
                        elseif DCH_Driver_Taliana_Martinez2 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 2)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 1)
                        elseif DCH_Driver_Taliana_Martinez3 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 2)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 2)
                        elseif DCH_Driver_Taliana_Martinez4 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 2)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 3)
                        elseif DCH_Driver_Eddie_Toh1 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 3)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 0)
                        elseif DCH_Driver_Eddie_Toh2 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 3)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 1)
                        elseif DCH_Driver_Eddie_Toh3 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 3)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 2)
                        elseif DCH_Driver_Eddie_Toh4 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 3)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 3)
                        elseif DCH_Driver_Zach_Nelson1 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 4)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 0)
                        elseif DCH_Driver_Zach_Nelson2 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 4)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 1)
                        elseif DCH_Driver_Zach_Nelson3 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 4)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 2)
                        elseif DCH_Driver_Zach_Nelson4 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 4)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 3)
                        elseif DCH_Driver_Chester_McCoy1 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 5)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 0)
                        elseif DCH_Driver_Chester_McCoy2 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 5)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 1)
                        elseif DCH_Driver_Chester_McCoy3 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 5)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 2)
                        elseif DCH_Driver_Chester_McCoy4 then
                            stats.set_int(getMP() .. "H3OPT_CREWDRIVER", 5)
                            stats.set_int(getMP() .. "H3OPT_VEHS", 3)
                        end
                        
                        locals.set_int("gb_casino_heist_planning", DCRBl, 2)
                    end
                    ImGui.TreePop()
                end
                if ImGui.TreeNode("Hacker Options") then
                    DCH_Hacker_Rickie_Lukens = ImGui.Checkbox("Rickie Lukens", DCH_Hacker_Rickie_Lukens)
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip("Skill: Poor\nCut: 3%\nTime Undetected: 2:26")
                    end
                    if DCH_Hacker_Rickie_Lukens then
                        DCH_Hacker_Christian_Feltz = false
                        DCH_Hacker_Yohan_Blair = false
                        DCH_Hacker_Avi_Schwartzman = false
                        DCH_Hacker_Page_Harris = false
                    end
        
                    
                    DCH_Hacker_Christian_Feltz = ImGui.Checkbox("Christian Feltz", DCH_Hacker_Christian_Feltz)
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip("Skill: Good\nCut: 5%\nTime Undetected: 2:52")
                    end
                    if DCH_Hacker_Christian_Feltz then
                        DCH_Hacker_Rickie_Lukens = false
                        DCH_Hacker_Yohan_Blair = false
                        DCH_Hacker_Avi_Schwartzman = false
                        DCH_Hacker_Page_Harris = false
                    end
        
                    
                    DCH_Hacker_Yohan_Blair = ImGui.Checkbox("Yohan Blair", DCH_Hacker_Yohan_Blair)
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip("Skill: Good\nCut: 7%\nTime Undetected: 2:59")
                    end
                    if DCH_Hacker_Yohan_Blair then
                        DCH_Hacker_Rickie_Lukens = false
                        DCH_Hacker_Christian_Feltz = false
                        DCH_Hacker_Avi_Schwartzman = false
                        DCH_Hacker_Page_Harris = false
                    end
        
                    
                    DCH_Hacker_Avi_Schwartzman = ImGui.Checkbox("Avi Schwartzman", DCH_Hacker_Avi_Schwartzman)
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip("Skill: Expert\nCut: 10%\nTime Undetected: 3:30")
                    end
                    if DCH_Hacker_Avi_Schwartzman then
                        DCH_Hacker_Rickie_Lukens = false
                        DCH_Hacker_Christian_Feltz = false
                        DCH_Hacker_Yohan_Blair = false
                        DCH_Hacker_Page_Harris = false
                    end
        
                    
                    DCH_Hacker_Page_Harris = ImGui.Checkbox("Page Harris", DCH_Hacker_Page_Harris)
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip("Skill: Expert\nCut: 9%\nTime Undetected: 3:26")
                    end
                    if DCH_Hacker_Page_Harris then
                        DCH_Hacker_Rickie_Lukens = false
                        DCH_Hacker_Christian_Feltz = false
                        DCH_Hacker_Yohan_Blair = false
                        DCH_Hacker_Avi_Schwartzman = false
                    end
        
                    DCH_Hacker_Button = ImGui.Button("Confirm Hacker")
                    if DCH_Hacker_Button then
                        if DCH_Hacker_Rickie_Lukens then
                            stats.set_int(getMP() .. "H3OPT_CREWHACKER", 1)
                        elseif DCH_Hacker_Christian_Feltz then
                            stats.set_int(getMP() .. "H3OPT_CREWHACKER", 2)
                        elseif DCH_Hacker_Yohan_Blair then
                            stats.set_int(getMP() .. "H3OPT_CREWHACKER", 3)
                        elseif DCH_Hacker_Avi_Schwartzman then
                            stats.set_int(getMP() .. "H3OPT_CREWHACKER", 4)
                        elseif DCH_Hacker_Page_Harris then
                            stats.set_int(getMP() .. "H3OPT_CREWHACKER", 5)
                        end
                        
                        locals.set_int("gb_casino_heist_planning", DCRBl, 2)
                    end
                    ImGui.TreePop()
                end
                ImGui.Separator()
                    
                    
                ImGui.SeparatorText("* PREPERATION *")
                DCH_Confirm_Preps_Button = ImGui.Button("Confirm All Prep Work")
                if DCH_Confirm_Preps_Button then
                    stats.set_int(getMP() .. "H3OPT_DISRUPTSHIP", 3)
                    stats.set_int(getMP() .. "H3OPT_KEYLEVELS", 2)
                    stats.set_int(getMP() .. "H3OPT_BITSET0", -1)
                    stats.set_int(getMP() .. "H3OPT_BITSET1", -1)
                    stats.set_int(getMP() .. "H3OPT_COMPLETEDPOSIX", -1)
                end
                ImGui.Separator()

                if ImGui.TreeNode("During Heist") then
                    DCH_Heist_Remove_Crew_Cut = ImGui.Button("Remove Crew's Cut")
                    ImGui.SameLine()
                    ImGui.TextDisabled("(?)")
                    if ImGui.IsItemHovered() then
                        ImGui.SetTooltip(" - Changes Lester's Cut to $0\n - Changes Hacker's Cut to $0\n - Changes Driver's Cut to $0\n - Changes Gunman's Cut to $0")
                    end
                    if DCH_Heist_Remove_Crew_Cut then
                        tunables.set_int("CH_LESTER_CUT", 0) -- Lester's Cut

                        tunables.set_int("HEIST3_HACKERS_RICKIE_CUT", 0)
                        tunables.set_int("HEIST3_HACKERS_CHRISTIAN_CUT", 0)
                        tunables.set_int("HEIST3_HACKERS_YOHAN_CUT", 0)
                        tunables.set_int("HEIST3_HACKERS_AVI_CUT", 0)
                        tunables.set_int("HEIST3_HACKERS_PAIGE_CUT", 0)

                        tunables.set_int("HEIST3_PREPBOARD_GUNMEN_KARL_CUT", 0)
                        tunables.set_int("HEIST3_PREPBOARD_GUNMEN_GUSTAVO_CUT", 0)
                        tunables.set_int("HEIST3_PREPBOARD_GUNMEN_CHARLIE_CUT", 0)
                        tunables.set_int("HEIST3_PREPBOARD_GUNMEN_CHESTER_CUT", 0)
                        tunables.set_int("HEIST3_PREPBOARD_GUNMEN_PATRICK_CUT", 0)

                        tunables.set_int("HEIST3_DRIVERS_KARIM_CUT", 0)
                        tunables.set_int("HEIST3_DRIVERS_TALIANA_CUT", 0)
                        tunables.set_int("HEIST3_DRIVERS_EDDIE_CUT", 0)
                        tunables.set_int("HEIST3_DRIVERS_ZACH_CUT", 0)
                        tunables.set_int("HEIST3_DRIVERS_CHESTER_CUT", 0)
                    end
                    
                    DCH_Heist_Bypass_Fingerprint_Hack = ImGui.Button("Bypass Fingerprint Hack")
                    if DCH_Heist_Bypass_Fingerprint_Hack then
                        if locals.get_int("fm_mission_controller", 53087) == 4 then
                            locals.set_int("fm_mission_controller", 53087, 5)
                        end
                    end
                    
                    DCH_Heist_Bypass_Keypad_Hack = ImGui.Button("Bypass Keypad Hack")
                    if DCH_Heist_Bypass_Keypad_Hack then
                        if locals.get_int("fm_mission_controller", 54153) ~= 4 then
                            locals.set_int("fm_mission_controller", 54153, 5)
                        end
                    end
                    
                    DCH_Heist_Bypass_Vault_Door_Drill = ImGui.Button("Bypass Vault Door Drill")
                    if DCH_Heist_Bypass_Vault_Door_Drill then
                        locals.set_int("fm_mission_controller", 10143 + 7, locals.get_int("fm_mission_controller", 10143 + 37))
                    end
                    ImGui.TreePop()
                end

                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Doomsday") then
                ImGui.SeparatorText("* SETUPS *")
                DDH_Act_One_Setup = ImGui.Checkbox("Act: I", DDH_Act_One_Setup)
                if DDH_Act_One_Setup then
                    DDH_Act_Two_Setup = false
                    DDH_Act_Three_Setup = false
                end
                DDH_Act_Two_Setup = ImGui.Checkbox("Act: II", DDH_Act_Two_Setup)
                if DDH_Act_Two_Setup then
                    DDH_Act_One_Setup = false
                    DDH_Act_Three_Setup = false
                end
                DDH_Act_Three_Setup = ImGui.Checkbox("Act: III", DDH_Act_Three_Setup)
                if DDH_Act_Three_Setup then
                    DDH_Act_One_Setup = false
                    DDH_Act_Two_Setup = false
                end
    
                DDH_Setup_Button = ImGui.Button("Confirm Set-up")
                if DDH_Setup_Button then
                    if DDH_Act_One_Setup then
                        stats.set_int(getMP() .. "GANGOPS_FLOW_MISSION_PROG", 7)
                        stats.set_int(getMP() .. "GANGOPS_FM_MISSION_PROG", 7)
                    elseif DDH_Act_Two_Setup then
                        stats.set_int(getMP() .. "GANGOPS_FLOW_MISSION_PROG", 240)
                        stats.set_int(getMP() .. "GANGOPS_FM_MISSION_PROG", 248)
                    elseif DDH_Act_Three_Setup then
                        stats.set_int(getMP() .. "GANGOPS_FLOW_MISSION_PROG", 15872)
                        stats.set_int(getMP() .. "GANGOPS_FM_MISSION_PROG", 16128)
                    end
                    stats.set_int(getMP() .. "GANGOPS_FM_MISSION_PROG", -1)
                end

                   
                ImGui.Separator()
                ImGui.SeparatorText("* CUTS *")
                DDH_Max_All_Cuts_Button = ImGui.Button("100% for all Player's Cuts")
                if DDH_Setup_Button then
                    globals.set_int(1960755 + 812 + 50 + 1, 100)
                    globals.set_int(1960755 + 812 + 50 + 2, 100)
                    globals.set_int(1960755 + 812 + 50 + 3, 100)
                    globals.set_int(1960755 + 812 + 50 + 4, 100)
                end

                if ImGui.TreeNode("During Heist") then

                    ImGui.SeparatorText("Bypass ACT: III Hack")
                    DDH_Heist_ACTIII_Hack_Bypass = ImGui.Button("Bypass ACT: III Hack")
                    if DDH_Heist_ACTIII_Hack_Bypass then
                        locals.set_int("fm_mission_controller", 1292 + 135, 3)
                    end

                    ImGui.Separator()
                    ImGui.SeparatorText("Instant Finish Heist")
                    DDH_Insta_Finish_Button = ImGui.Button("Instant Finish")
                    if DDH_Insta_Finish_Button then
                        locals.set_int("fm_mission_controller", 19746, 12)
                        locals.set_int("fm_mission_controller", 19746 + 2686, 10000000)
                        locals.set_int("fm_mission_controller", 28400 + 1, 99999)
                        locals.set_int("fm_mission_controller", 31656 + 69, 99999)
                    end
                    ImGui.TreePop()
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Cayo Perico") then
                ImGui.EndTabItem()
            end
            ImGui.EndTabBar()
        end
    else
        ImGui.Text("Not available in singleplayer.")
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------





------------------------------------------------------------------------------------------------------------------------------------------------------
GunVanMenu = menu:add_tab(" - Gun Van")
GunVanMenu:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar(" - Gun Van") then

            if ImGui.BeginTabItem("WEAPONS") then
                GV_Disable_Proximity_Blip = ImGui.Button("Disable Proximity Blip")
                if GV_Disable_Proximity_Blip then
                    tunables.set_float(15999531, 500.0)
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Disable's the need to be within range of the Gun Van for it to appear on the map.")
                end


                ImGui.SeparatorText("WEAPONS")
                GV_Weapon_Discount = ImGui.Button("100% Discount")
                if GV_Weapon_Discount then
                    for i = 0, 9 do
                        tunables.set_float("XM22_GUN_VAN_SLOT_WEAPON_DISCOUNT_" .. i, 1)
                    end
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Applies 100% Discount to all Weapons.")
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("THROWABLE") then
                GV_Disable_Proximity_Blip = ImGui.Button("Disable Proximity Blip")
                if GV_Disable_Proximity_Blip then
                    tunables.set_float(15999531, 500.0)
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Disable's the need to be within range of the Gun Van for it to appear on the map.")
                end

                
                ImGui.SeparatorText("THROWABLE")
                GV_THROWABLE_Discount = ImGui.Button("100% Discount")
                if GV_THROWABLE_Discount then
                    for i = 0, 2 do
                        tunables.set_float("XM22_GUN_VAN_SLOT_THROWABLE_DISCOUNT_" .. i, 1)
                    end
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Applies 100% Discount to all Throwables.")
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("BODY ARMOR") then
                GV_Disable_Proximity_Blip = ImGui.Button("Disable Proximity Blip")
                if GV_Disable_Proximity_Blip then
                    tunables.set_float(15999531, 500.0)
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Disable's the need to be within range of the Gun Van for it to appear on the map.")
                end

                
                ImGui.SeparatorText("BODY ARMOR")
                GV_BODY_ARMOR_Discount = ImGui.Button("100% Discount")
                if GV_BODY_ARMOR_Discount then
                    for i = 0, 4 do
                        tunables.set_float("XM22_GUN_VAN_SLOT_ARMOUR_DISCOUNT_" .. i, 1)
                    end
                end
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("Applies 100% Discount to all Body Armors.")
                end
                ImGui.EndTabItem()
            end
        end
    else
        ImGui.Text("Not available in singleplayer.")
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------





------------------------------------------------------------------------------------------------------------------------------------------------------

Unlocks = menu:add_tab(" - Unlocks")
Unlocks:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar(" - Unlocks") then
            if ImGui.BeginTabItem("Tattoo Parlor") then
                ImGui.SeparatorText("Tattoos")
				TattooParlor_Unlocks = ImGui.Button("Unlock All Tattoos")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if TattooParlor_Unlocks then
                    stats.set_int(getMP() .. "TATTOO_FM_CURRENT_32", -1)
                    for i = 0, 53 do
                        stats.set_int(getMP() .. "TATTOO_FM_UNLOCKS_" .. i, -1)
                    end
                    stats.set_bool(getMP() .. "AWD_500_HEADSHOTS", true)
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Ammu Nation") then
                
                ImGui.SeparatorText("Melee Skins")
				Ammu_Nation_Melee_Skin_Unlocks = ImGui.Button("Unlock All Melee Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Melee_Skin_Unlocks then
                    stats.set_int(getMP() .. "UNARMED_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "KNIFE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "NIGHTSTICK_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "CROWBAR_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "SHOVEL_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "WRENCH_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "HAMMER_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "BAT_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "GCLUB_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "BOTTLE_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Pistol Skins")
				Ammu_Nation_Pistol_Skin_Unlocks = ImGui.Button("Unlock All Pistol Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Pistol_Skin_Unlocks then
                    stats.set_int(getMP() .. "PISTOL_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "CMBTPISTOL_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "PISTOL50_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "APPISTOL_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "SNSPISTOL_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("SMG Skins")
				Ammu_Nation_SMG_Skin_Unlocks = ImGui.Button("Unlock All SMG Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_SMG_Skin_Unlocks then
                    stats.set_int(getMP() .. "MICROSMG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "SMG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "ASLTSMG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "MG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "CMBTMG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "ASLTMG_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Rifle Skins")
				Ammu_Nation_Rifle_Skin_Unlocks = ImGui.Button("Unlock All Rifle Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Rifle_Skin_Unlocks then
                    stats.set_int(getMP() .. "ASLTRIFLE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "CRBNRIFLE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "ADVRIFLE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "BULLPUP_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Shotgun Skins")
                Ammu_Nation_Shotgun_Skin_Unlocks = ImGui.Button("Unlock All Shotgun Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Shotgun_Skin_Unlocks then
                    stats.set_int(getMP() .. "PUMP_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "SAWNOFF_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "ASLTSHTGN_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Stun Gun Skins")
                Ammu_Nation_Stun_Gun_Skin_Unlocks = ImGui.Button("Unlock All Stun Gun Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Stun_Gun_Skin_Unlocks then
                    stats.set_int(getMP() .. "STUNGUN_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Sniper Skins")
                Ammu_Nation_Sniper_Skin_Unlocks = ImGui.Button("Unlock All Sniper Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Sniper_Skin_Unlocks then
                    stats.set_int(getMP() .. "SNIPERRFL_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "HVYSNIPER_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Heavy Weapon Skins")
                Ammu_Nation_Heavy_Weapon_Skin_Unlocks = ImGui.Button("Unlock All Heavy Weapon Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Heavy_Weapon_Skin_Unlocks then
                    stats.set_int(getMP() .. "GRNLAUNCH_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "RPG_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "MINIGUNS_ENEMY_KILLS", 600)
                end
                
                ImGui.Separator()
                ImGui.SeparatorText("Throwable Skins")
                Ammu_Nation_Throwable_Skin_Unlocks = ImGui.Button("Unlock All Throwable Skins")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if Ammu_Nation_Throwable_Skin_Unlocks then
                    stats.set_int(getMP() .. "GRENADE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "SMKGRENADE_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "STKYBMB_ENEMY_KILLS", 600)
                    stats.set_int(getMP() .. "MOLOTOV_ENEMY_KILLS", 600)
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Los Santos Customs") then
                ImGui.SeparatorText("Paint Jobs")
                LSC_PaintJobs = ImGui.Button("Unlock All Paint Jobs")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if LSC_PaintJobs then
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_1_UNLCK", -1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_2_UNLCK",-1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_3_UNLCK", -1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_4_UNLCK", -1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_5_UNLCK", -1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_6_UNLCK", -1)
                    stats.set_int(getMP() .. "CHAR_FM_CARMOD_7_UNLCK", -1)
                    stats.set_int(getMP() .. "AWD_WIN_CAPTURES", 50)
                    stats.set_int(getMP() .. "AWD_DROPOFF_CAP_PACKAGES", 100)
                    stats.set_int(getMP() .. "AWD_KILL_CARRIER_CAPTURE", 100)
                    stats.set_int(getMP() .. "AWD_FINISH_HEISTS", 50)
                    stats.set_int(getMP() .. "AWD_FINISH_HEIST_SETUP_JOB", 50)
                    stats.set_int(getMP() .. "AWD_NIGHTVISION_KILLS", 100)
                    stats.set_int(getMP() .. "AWD_WIN_LAST_TEAM_STANDINGS", 50)
                    stats.set_int(getMP() .. "AWD_ONLY_PLAYER_ALIVE_LTS", 50)
                    stats.set_int(getMP() .. "AWD_FMRALLYWONDRIVE", 25)
                    stats.set_int(getMP() .. "AWD_FMRALLYWONNAV", 25)
                    stats.set_int(getMP() .. "AWD_FMWINSEARACE", 25)
                    stats.set_int(getMP() .. "AWD_RACES_WON", 50)
                    stats.set_int(getMP() .. "MOST_FLIPS_IN_ONE_JUMP", 5)
                    stats.set_int(getMP() .. "MOST_SPINS_IN_ONE_JUMP", 5)
                    stats.set_int(getMP() .. "NUMBER_SLIPSTREAMS_IN_RACE", 100)
                    stats.set_int(getMP() .. "NUMBER_TURBO_STARTS_IN_RACE", 50)
                    stats.set_int(getMP() .. "RACES_WON", 50)
                    stats.set_int(getMP() .. "USJS_COMPLETED", 50)
                    stats.set_int(getMP() .. "AWD_FM_GTA_RACES_WON", 50)
                    stats.set_int(getMP() .. "AWD_FM_RACE_LAST_FIRST", 25)
                    stats.set_int(getMP() .. "AWD_FM_RACES_FASTEST_LAP", 50)
                    stats.set_int(getMP() .. "AWD_FMBASEJMP", 25)
                    stats.set_int(getMP() .. "AWD_FMWINAIRRACE", 25)
                    stats.set_int("MPPLY_TOTAL_RACES_WON", 50)
                end

                
                ImGui.Separator()
                ImGui.SeparatorText("Los Santos Tuners")
                LSC_TunerWheels = ImGui.Button("Unlock All Track Wheels")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if LSC_TunerWheels then
                    Tuners2 = {11, 26, 41, 56}
                    Tuners3 = {5, 10, 15, 20, 25}

                    stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL1", true, 60) -- Dinka SPL

                    for index = 1, #Tuners2 do
                        stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL2", true, Tuners2[index])
                    end

                    for index = 1, #Tuners3 do
                        stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL3", true, Tuners3[index])
                    end
                end
                LSC_TunerLiveries = ImGui.Button("Unlock All Tuner Liveries")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if LSC_TunerLiveries then
                    Tuners2 = {1, 6, 16,21,  31, 36, 46, 51, 61}
                    Tuners3 = {2, 7, 12, 17, 22, 27, 32, 34, 37, 39, 42, 44, 47, 49, 52, 54, 57, 59, 62}
                    Tuners4 = {0, 3, 5, 8, 10, 13, 15, 18, 20, 23, 25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53}



                    for index = 1, #Tuners2 do
                        stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL2", true, Tuners2[index])
                    end



                    for index = 1, #Tuners3 do
                        stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL3", true, Tuners3[index])
                    end



                    for index = 1, #Tuners4 do
                        stats.set_bool_masked(getMP() .. "TUNERPSTAT_BOOL4", true, Tuners4[index])
                    end
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Arena Wars") then

                ImGui.SeparatorText("Prebuild Trade Prices")
                ArenaWar_TradePrice_Apocalypse_Unlock = ImGui.Button("Unlock All Apocalypse Vehicle Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Apocalypse_Unlock then
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 1) -- Apocalypse Cerberus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 3) -- Apocalypse Brutus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 5) -- Apocalypse ZR380
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 12) -- Apocalypse Scarab
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 17) -- Apocalypse Imperator
				end

				ArenaWar_TradePrice_Future_Shock_Unlock = ImGui.Button("Unlock All Future Shock Vehicle Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Future_Shock_Unlock then
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 2) -- Future Shock Cerberus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 6) -- Future Shock Brutus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 1) -- Future Shock Scarab
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 18) -- Future Shock Imperator
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 15) -- Future Shock ZR380
				end

				ArenaWar_TradePrice_Nightmare_Unlock = ImGui.Button("Unlock All Nightmare Vehicle Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Nightmare_Unlock then
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 4) -- Nightmare Cerberus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 11) -- Nightmare Brutus
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 14) -- Nightmare Scarab
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 19) -- Nightmare Imperator
					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, 16) -- Nightmare ZR380
				end


                ImGui.Separator()
                ImGui.SeparatorText("Upgradable Trade Prices")
				ArenaWar_TradePrice_Upgradable_Unlock = ImGui.Button("Unlock All Upgradable Vehicle Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Upgradable_Unlock then
					Upgradeable_Vehicles = {7, 10, 11, 12, 13, 14, 16}

					for index = 1, #Upgradeable_Vehicles do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, Upgradeable_Vehicles[index])
					end
                end


                ImGui.Separator()
                ImGui.SeparatorText("Headlight Trade Prices")
				ArenaWar_TradePrice_Headlight_Unlock = ImGui.Button("Unlock All Headlight Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Headlight_Unlock then
					Headlights = {18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29}

					for index = 1, #Headlights do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, Headlights[index])
					end
                end


                ImGui.Separator()
                ImGui.SeparatorText("Upgrade Trade Prices")
				ArenaWar_TradePrice_Upgrade_Unlock = ImGui.Button("Unlock All Upgrade Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Upgrade_Unlock then

					stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, 17)

					Upgrades2 = {21, 22, 27, 28, 29, 35, 37, 38, 39, 46, 49, 50, 51, 58, 61, 62, 63}
					for index = 1, #Upgrades2 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL2", true, Upgrades2[index])
					end

					Upgrades3 = {6, 7, 8, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63}
					for index = 1, #Upgrades3 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL3", true, Upgrades3[index])
					end

					Upgrades4 = {0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}
					for index = 1, #Upgrades4 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL4", true, Upgrades4[index])
					end

					Upgrades6 = {26, 30, 34, 35, 38, 39, 41, 42, 43, 48, 49, 50, 51, 52, 53, 54, 61, 62, 63}
					for index = 1, #Upgrades6 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL6", true, Upgrades6[index])
					end

					Upgrades7 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63}
					for index = 1, #Upgrades7 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL7", true, Upgrades7[index])
					end

					Upgrades8 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37}
					for index = 1, #Upgrades8 do
						stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL8", true, Upgrades8[index])
					end
                end


                ImGui.Separator()
                ImGui.SeparatorText("Pegasus Trade Prices")
				ArenaWar_TradePrice_Pegasus_Unlock = ImGui.Button("Unlock All Pegasus Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Pegasus_Unlock then
                    ArenaWars_Pegasus_Vehicles = {30, 31, 32, 33, 34, 35, 36, 37}
    
                    for index = 1, #ArenaWars_Pegasus_Vehicles do
                        stats.set_bool_masked(getMP() .. "ARENAWARSPSTAT_BOOL0", true, ArenaWars_Pegasus_Vehicles[index])
                    end
                end


                ImGui.Separator()
                ImGui.SeparatorText("Outfits Trade Prices")
				ArenaWar_TradePrice_Outfits_Unlock = ImGui.Button("Unlock All Outfits Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if ArenaWar_TradePrice_Outfits_Unlock then
                    stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL3", true, 24)
                    stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL0", true, 8)
                    stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL0", true, 15)
                    stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL0", true, 38)
                    for i = 7, 63 do
                        stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL4", true, i)
                    end
                    for i = 0, 63 do
                        stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL5", true, i)
                    end
                    for i = 0, 47 do
                        stats.set_bool_masked(getMP() .. "_ARENAWARSPSTAT_BOOL6", true, i)
                    end
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Diamond Casino") then
                ImGui.SeparatorText("Outfits")
				DCH_Unlocks_Outfit_All = ImGui.Button("Unlock All Outfits")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if DCH_Unlocks_Outfit_All then
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL1", true, 63) -- Refuse Collectors
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 0) -- Undertakers
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 1) -- Valet Outfits
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 3) -- Prison Guards
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 4) -- FIB Suits
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 6) -- Gruppe Sechs Gear
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 7) -- Bugstars Uniforms
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 8) -- Maintenance
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 9) -- Yung Ancestors
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 10) -- Firefighter Gear
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 11) -- Orderly Armor
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 12) -- Upscale Armor
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 13) -- Evening Armor
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 14) -- Reinforced: Padded Combat
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 15) -- Reinforced: Bulk Combat
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 16) -- Reinforced: Compact Combat
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 17) -- Balaclava Crook
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 18) -- Classic Crook
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 19) -- High-end Crook
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 20) -- Infiltration: Upgraded Tech
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 21) -- Infiltration: Advanced Tech
                    stats.set_bool_masked(getMP() .. "CASINOHSTPSTAT_BOOL2", true, 22) -- Infiltration: Modernized Tech
                end
                ImGui.EndTabItem()
            end



            if ImGui.BeginTabItem("Agents Of Sabotage") then
                ImGui.SeparatorText("Police Cars")
				AOS_Unlocks_Police_Car_Trade_Prices = ImGui.Button("Unlock Police Car Trade Prices")
                ImGui.SameLine()
                ImGui.TextDisabled("(?)")
                if ImGui.IsItemHovered() then
                    ImGui.SetTooltip("For Permanent unlock, change session after done")
                end
                if AOS_Unlocks_Police_Car_Trade_Prices then
                    for i = 32319, 32323 do
                        stats.set_packed_stat_bool(i, true)
                    end
                    for i = 42280, 42284 do
                        stats.set_packed_stat_bool(i, true)
                    end
                    stats.set_int(getMP() .. "SALV23_SCOPE_BS", -1)
                end
                ImGui.EndTabItem()
            end
        end
    else
        ImGui.Text("Not available in singleplayer.")
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------





------------------------------------------------------------------------------------------------------------------------------------------------------
ReportsMenu = menu:add_tab(" - Reports Menu")
ReportsMenu:add_imgui(function()
    if network.is_session_started() then
        if ImGui.BeginTabBar(" - Reports Menu") then
            if ImGui.BeginTabItem("Commendations") then
                ImGui.Text("Friendly: " .. stats.get_int("MPPLY_FRIENDLY"))
                ImGui.Text("Helpful: " .. stats.get_int("MPPLY_HELPFUL"))
                ImGui.EndTabItem()
            end
            if ImGui.BeginTabItem("Crew") then
                ImGui.Text("Bad Crew Name: " .. stats.get_int("MPPLY_BAD_CREW_NAME"))
                ImGui.Text("Bad Crew Motto: " .. stats.get_int("MPPLY_BAD_CREW_MOTTO"))
                ImGui.Text("Bad Crew Status: " .. stats.get_int("MPPLY_BAD_CREW_STATUS"))
                ImGui.Text("Bad Crew Emblem: " .. stats.get_int("MPPLY_BAD_CREW_EMBLEM"))
                ImGui.EndTabItem()
            end
            if ImGui.BeginTabItem("Bad Player") then
                ImGui.Text("Griefing: " .. stats.get_int("MPPLY_GRIEFING"))
                ImGui.Text("Exploiting: " .. stats.get_int("MPPLY_EXPLOITS"))
                ImGui.Text("Abusing Bugs: " .. stats.get_int("MPPLY_GAME_EXPLOITS"))
                ImGui.Text("Annoying People In Text: " .. stats.get_int("MPPLY_TC_ANNOYINGME"))
                ImGui.Text("Hate Speech In Text: " .. stats.get_int("MPPLY_TC_HATE"))
                ImGui.Text("Annoying People In Voice: " .. stats.get_int("MPPLY_VC_ANNOYINGME"))
                ImGui.Text("Hate Speech In Voice: " .. stats.get_int("MPPLY_VC_HATE"))
                ImGui.Text("Offensive Language: " .. stats.get_int("MPPLY_OFFENSIVE_LANGUAGE"))
                ImGui.Text("Offensive Tagplate: " .. stats.get_int("MPPLY_OFFENSIVE_TAGPLATE"))
                ImGui.Text("Offensive Content: " .. stats.get_int("MPPLY_OFFENSIVE_UGC"))
                ImGui.EndTabItem()
            end
        end
    else
        ImGui.Text("Not available in singleplayer.")
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------





------------------------------------------------------------------------------------------------------------------------------------------------------
CreditsMenu = menu:add_tab(" - Credits")
CreditsMenu:add_imgui(function()
    if ImGui.BeginTabBar(" - Credits") then
        if ImGui.BeginTabItem("Credits") then
            ImGui.Text("Silent")
            ImGui.Text("KillaB")
            ImGui.EndTabItem()
        end
    end
end)
------------------------------------------------------------------------------------------------------------------------------------------------------