-- Lua Filter allowing "raw" code blocks to be interpreted as LaTeX.
-- Copyright (c) 2019 - Romain WALLON, released under MIT license.

function CodeBlock(block)
    if block.classes[1] == "rst"
    then
        -- Converting this code block to a raw LaTeX block.
        return { pandoc.RawBlock("rst", block.text), pandoc.Para{} }
    end

    -- This code block is left as is.
    return block
end
