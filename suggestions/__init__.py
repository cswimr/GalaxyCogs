from .suggestions import Suggestions


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
