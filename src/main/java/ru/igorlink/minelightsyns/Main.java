package ru.igorlink.minelightsyns;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;

public class Main extends JavaPlugin {

    @Override
    public void onEnable() {
        getCommand("lightsync").setExecutor((sender, command, label, args) -> {

            //Если у команды больше одного аргумента - это ошибка (у нашей команды должен быть один аргумент - ник игрока), возвращаем код E0
            if (args.length > 1) {
                sender.sendMessage("E0");
                return false;
            }

            //Если игрок с указанным ником не найден, возвращаем код ошибки E1
            String username = args[0];
            Player player = getServer().getPlayer(username); //Получаем объект игрока
            if (player == null || !player.isOnline()) {
                sender.sendMessage("E1");
                return false;
            }

            Location top_block_cords = player.getEyeLocation(); //Координаты блока с нашей головой - это на 1 выше, чем координаты игрока
            //Если успешно получили координаты игрока...
            if (top_block_cords != null) {
                byte light_level = top_block_cords.getBlock().getLightLevel(); //Получаем уровень освещенности блока с головой игрока
                sender.sendMessage(String.valueOf(light_level)); //Отправляем этот уровень освещенности отправителю команды (в нашем проекте это будет программа на питоне, которая будет вызывать команды через rcon)
            }
            return false;
        });
    }

}