package ru.igorlink.minelightsyns;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

public class Main extends JavaPlugin {
    //При вызове нашей команды
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        //Если у команды больше одного аргумента - это ошибка (у нашей команды должен быть один аргумент - ник игрока), возвращаем код E0
        if (args.length > 1) {
            sender.sendMessage("E0");
            return false;
        }

        //Если игрок с указанным ником не найден, возвращаем код ошибки E1
        String username = args[0];
        Player player = getServer().getPlayer(username); //Получаем объект игрока
        if (player == null || !player.isOnline()) { //может случиться так, что какой-то говноплагин держит объект даже при выходе, лучше сделать еще проверку на онлайн
            sender.sendMessage("E1");
            return false;
        }

        Location top_block_cords = player.getEyeLocation(); //Координаты блока с нашей головой - это на 1 выше, чем координаты игрока
        byte light_level = top_block_cords.getBlock().getLightLevel(); //Получаем уровень освещенности блока с головой игрока
        sender.sendMessage(String.valueOf(light_level)); //Отправляем этот уровень освещенности отправителю команды (в нашем проекте это будет программа на питоне, которая будет вызывать команды через rcon)
        return true;
    }
}