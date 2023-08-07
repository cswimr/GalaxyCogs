from .info import Info


async def setup(bot):
    await bot.add_cog(Info(bot))
