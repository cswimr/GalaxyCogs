from .shortmute import Shortmute


async def setup(bot):
    await bot.add_cog(Shortmute(bot))
