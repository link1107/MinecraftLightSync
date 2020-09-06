package ru.igorlink.minelightsyns;

import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;


public class Main extends JavaPlugin implements Listener {
    //При вызове нашей команды
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {

        //Если у команды больше одного аргумента - это ошибка (у нашей команды должен быть один аргумент - ник игрока), возвращаем код E0
        if (args.length > 1) {
            sender.sendMessage("E0");
            return true; //Выходим
        }

        //Если игрок с указанным ником не найден, возвращаем код ошибки E1
        String username = args[0];
        if (getServer().getPlayer(username) == null) {
            sender.sendMessage("E1");
            return true; //Выходим
        }

        //Получаем уровень освещенности блока с головой игрока
        final int lightLevel = getServer().getPlayer(username)
                .getEyeLocation()
                .getBlock()
                .getLightLevel();

        //Отправляем этот уровень освещенности отправителю команды (в нашем проекте это будет программа на питоне, которая будет вызывать команды через rcon)
        sender.sendMessage(String.valueOf(lightLevel));
        return true; //Выходим
    }

}
