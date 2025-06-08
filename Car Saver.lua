gui.createMainTab("Car Saver")
gui.addButton("Mark Car As Saveable", "Make current vehicle saveable to a garage.", function()
	script.queue(function()
		local vehicle = util.getLocalVehicleHandle()
		if vehicle ~= 0 then
			VEHICLE.SET_VEHICLE_HAS_BEEN_OWNED_BY_PLAYER(vehicle, true)
			VEHICLE.SET_VEHICLE_CAN_SAVE_IN_GARAGE(vehicle, true)
			gui.pushNotification("Activated!", "Vehicle can be saved to garage!")
		else
			gui.pushNotification("Failed!", "Player not in a vehicle!")
		end
	end)
end)