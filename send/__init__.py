from .send import Send


async def setup(bot):
    await bot.add_cog(Send(bot))
